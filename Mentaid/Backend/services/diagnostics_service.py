import os
import uuid
import csv
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestRegressor


class DiagnosticsService:
    """
    Lightweight diagnostic service that:
    - Loads the synthetic DSM-5/ICD-aware dataset
    - Trains a simple text classifier to predict disorder_type from journal_text
    - Trains a regressor to approximate total_score
    - Provides an interactive yes/no triage when free text is insufficient
    - Persists predictions to a CSV file for later analysis
    """

    def __init__(self) -> None:
        # Resolve dataset paths relative to repo root
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(backend_dir, os.pardir, os.pardir))

        # Primary dataset provided by the user (200 rows)
        candidate_paths = [
            os.path.join(repo_root, "agent", "mock_data", "mental_health_comprehensive_dataset.csv"),
            os.path.join(repo_root, "Mentaid", "Backend", "data", "mental_health_comprehensive_dataset.csv"),
        ]
        dataset_path = next((p for p in candidate_paths if os.path.exists(p)), None)
        if dataset_path is None:
            raise FileNotFoundError(
                "mental_health_comprehensive_dataset.csv not found in expected locations"
            )

        # Optional balanced test set
        candidate_test_paths = [
            os.path.join(repo_root, "agent", "mock_data", "mental_health_comprehensive_balanced_test.csv"),
            os.path.join(repo_root, "Mentaid", "Backend", "data", "mental_health_comprehensive_balanced_test.csv"),
        ]
        self.balanced_test_path = next((p for p in candidate_test_paths if os.path.exists(p)), None)

        # Where to save predictions
        self.output_dir = os.path.join(repo_root, "Mentaid", "Backend", "data")
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_csv = os.path.join(self.output_dir, "diagnostic_results.csv")

        # Load dataset
        self.df = pd.read_csv(dataset_path)
        # Clean up minimal columns
        self.df = self.df.dropna(subset=["journal_text", "disorder_type"])  # keep only rows with text and label

        # Prepare models
        self._prepare_models()

        # Interactive triage state
        self.sessions: Dict[str, Dict] = {}

    def _prepare_models(self) -> None:
        # Text -> disorder_type classifier
        self.classifier_pipeline: Pipeline = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=8000, min_df=1)),
                ("clf", LogisticRegression(max_iter=2000, n_jobs=None, solver="lbfgs", multi_class="auto")),
            ]
        )

        self.classifier_pipeline.fit(self.df["journal_text"], self.df["disorder_type"]) 

        # Text -> total_score regressor (fallback to 0 if not available)
        if "total_score" in self.df.columns:
            df_reg = self.df.dropna(subset=["total_score"]).copy()
            # Guard for non-numeric artifacts
            def _to_float(x):
                try:
                    return float(x)
                except Exception:
                    return None
            df_reg["total_score_num"] = df_reg["total_score"].apply(_to_float)
            df_reg = df_reg.dropna(subset=["total_score_num"])  # keep numeric

            self.reg_vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=8000, min_df=1)
            X_reg = self.reg_vectorizer.fit_transform(df_reg["journal_text"])  
            y_reg = df_reg["total_score_num"].astype(float).values

            self.regressor = RandomForestRegressor(n_estimators=150, random_state=42)
            self.regressor.fit(X_reg, y_reg)
        else:
            self.reg_vectorizer = None
            self.regressor = None

        # Text -> severity_level classifier if available
        if "severity_level" in self.df.columns:
            df_sev = self.df.dropna(subset=["severity_level"])  
            self.severity_pipeline: Optional[Pipeline] = Pipeline(
                steps=[
                    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=8000, min_df=1)),
                    ("clf", LogisticRegression(max_iter=2000, n_jobs=None, solver="lbfgs", multi_class="auto")),
                ]
            )
            self.severity_pipeline.fit(df_sev["journal_text"], df_sev["severity_level"])
        else:
            self.severity_pipeline = None

    # ---------------------- Persistence ----------------------
    def _write_result_row(self, row: Dict) -> None:
        fieldnames = [
            "entry_id",
            "user_id",
            "timestamp",
            "journal_text",
            "method",
            "predicted_disorder",
            "total_score",
            "severity_level",
            "meets_diagnostic_threshold",
            "risk_level",
        ]
        file_exists = os.path.exists(self.output_csv)
        with open(self.output_csv, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({k: row.get(k) for k in fieldnames})

    # ---------------------- Public API ----------------------
    def predict_from_text(self, user_id: str, journal_text: str) -> Dict:
        """
        Predict disorder and score from free text. Persist result to CSV.
        """
        predicted_disorder = self.classifier_pipeline.predict([journal_text])[0]

        # Score prediction
        if self.regressor is not None and self.reg_vectorizer is not None:
            X = self.reg_vectorizer.transform([journal_text])
            total_score_pred = float(self.regressor.predict(X)[0])
        else:
            total_score_pred = 0.0

        # Severity prediction or mapping
        if self.severity_pipeline is not None:
            severity_level = str(self.severity_pipeline.predict([journal_text])[0])
        else:
            # Map raw score to rough severity
            severity_level = self._map_score_to_severity(total_score_pred, predicted_disorder)

        meets_threshold = self._meets_threshold(severity_level, predicted_disorder, journal_text)
        risk_level = self._risk_from_context(predicted_disorder, severity_level, journal_text)

        result = {
            "entry_id": str(uuid.uuid4()),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "journal_text": journal_text,
            "method": "text",
            "predicted_disorder": predicted_disorder,
            "total_score": round(float(total_score_pred), 2),
            "severity_level": severity_level,
            "meets_diagnostic_threshold": bool(meets_threshold),
            "risk_level": risk_level,
        }

        self._write_result_row(result)
        return result

    # ---------------------- Interactive flow ----------------------
    def start_interactive(self, user_id: str, context_text: Optional[str] = None) -> Dict:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "user_id": user_id,
            "answers": {},    # key -> bool
            "stage": "triage_suicide",
            "created_at": datetime.utcnow().isoformat(),
            "context_text": context_text or "",
        }
        question = "In the past 2 weeks, have you had thoughts of harming yourself or ending your life?"
        return {
            "session_id": session_id,
            "question": question,
            "options": ["yes", "no"],
        }

    def answer_interactive(self, session_id: str, answer: str) -> Dict:
        answer_norm = str(answer).strip().lower()
        if answer_norm not in {"yes", "no", "y", "n", "true", "false"}:
            return {"error": "Answer must be yes or no"}
        is_yes = answer_norm in {"yes", "y", "true"}

        if session_id not in self.sessions:
            return {"error": "Invalid session_id"}

        session = self.sessions[session_id]
        stage = session["stage"]

        # Record answer by stage
        session["answers"][stage] = is_yes

        # Flow logic
        if stage == "triage_suicide":
            if is_yes:
                session["stage"] = "suicide_plan"
                return {
                    "session_id": session_id,
                    "question": "Have you made a plan or prepared for a suicide attempt?",
                    "options": ["yes", "no"],
                }
            else:
                session["stage"] = "triage_psychosis"
                return {
                    "session_id": session_id,
                    "question": "Have you seen or heard things that others do not (hallucinations)?",
                    "options": ["yes", "no"],
                }

        if stage == "suicide_plan":
            if is_yes:
                # Immediate risk outcome
                return self._finalize_interactive(
                    session_id,
                    predicted_disorder="Suicidal_Ideation",
                    score=25,
                    severity="severe",
                    risk="immediate",
                )
            else:
                session["stage"] = "suicide_intent"
                return {
                    "session_id": session_id,
                    "question": "Do you feel you might act on these thoughts (intent)?",
                    "options": ["yes", "no"],
                }

        if stage == "suicide_intent":
            if is_yes:
                return self._finalize_interactive(
                    session_id,
                    predicted_disorder="Suicidal_Ideation",
                    score=22,
                    severity="severe",
                    risk="high",
                )
            else:
                # Proceed to psychosis triage
                session["stage"] = "triage_psychosis"
                return {
                    "session_id": session_id,
                    "question": "Have you seen or heard things that others do not (hallucinations)?",
                    "options": ["yes", "no"],
                }

        if stage == "triage_psychosis":
            session["psychosis_hallucinations"] = is_yes
            session["stage"] = "psychosis_delusions"
            return {
                "session_id": session_id,
                "question": "Have you had fixed beliefs that others are plotting against you (delusions)?",
                "options": ["yes", "no"],
            }

        if stage == "psychosis_delusions":
            session["psychosis_delusions"] = is_yes
            session["stage"] = "psychosis_duration"
            return {
                "session_id": session_id,
                "question": "Have these symptoms persisted for longer than 1 month?",
                "options": ["yes", "no"],
            }

        if stage == "psychosis_duration":
            session["psychosis_duration"] = is_yes
            # Decision for schizophrenia
            psychosis_yes = int(session.get("psychosis_hallucinations", False)) + int(session.get("psychosis_delusions", False))
            if psychosis_yes >= 1 and is_yes:
                return self._finalize_interactive(
                    session_id,
                    predicted_disorder="Schizophrenia",
                    score=18,
                    severity="moderate",
                    risk="moderate",
                )
            # Else go to depression screen (PHQ-2)
            session["stage"] = "depression_q1"
            return {
                "session_id": session_id,
                "question": "Over the last 2 weeks, have you felt down, depressed, or hopeless most days?",
                "options": ["yes", "no"],
            }

        if stage == "depression_q1":
            session["dep_q1"] = is_yes
            session["stage"] = "depression_q2"
            return {
                "session_id": session_id,
                "question": "Over the last 2 weeks, have you had little interest or pleasure in doing things?",
                "options": ["yes", "no"],
            }

        if stage == "depression_q2":
            session["dep_q2"] = is_yes
            dep_yes = int(session.get("dep_q1", False)) + int(session.get("dep_q2", False))
            if dep_yes >= 2:
                return self._finalize_interactive(
                    session_id,
                    predicted_disorder="Depression",
                    score=15,
                    severity="moderate",
                    risk="moderate",
                )
            # Else go to anxiety GAD-2
            session["stage"] = "anxiety_q1"
            return {
                "session_id": session_id,
                "question": "Over the last 2 weeks, have you felt nervous, anxious, or on edge?",
                "options": ["yes", "no"],
            }

        if stage == "anxiety_q1":
            session["anx_q1"] = is_yes
            session["stage"] = "anxiety_q2"
            return {
                "session_id": session_id,
                "question": "Over the last 2 weeks, have you been unable to stop or control worrying?",
                "options": ["yes", "no"],
            }

        if stage == "anxiety_q2":
            session["anx_q2"] = is_yes
            anx_yes = int(session.get("anx_q1", False)) + int(session.get("anx_q2", False))
            if anx_yes >= 2:
                return self._finalize_interactive(
                    session_id,
                    predicted_disorder="Anxiety",
                    score=12,
                    severity="moderate",
                    risk="moderate",
                )
            # Nothing triggered strongly
            return self._finalize_interactive(
                session_id,
                predicted_disorder="Undetermined",
                score=0,
                severity="minimal",
                risk="low",
            )

        # Default fallback
        return {"error": "Unknown stage"}

    def _finalize_interactive(self, session_id: str, predicted_disorder: str, score: int, severity: str, risk: str) -> Dict:
        session = self.sessions.get(session_id, {})
        user_id = session.get("user_id", "unknown")
        context_text = session.get("context_text", "")

        result = {
            "entry_id": str(uuid.uuid4()),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "journal_text": context_text,
            "method": "interactive",
            "predicted_disorder": predicted_disorder,
            "total_score": score,
            "severity_level": severity,
            "meets_diagnostic_threshold": bool(self._meets_threshold(severity, predicted_disorder, context_text)),
            "risk_level": risk,
        }
        self._write_result_row(result)

        # End session
        if session_id in self.sessions:
            del self.sessions[session_id]

        return {"final": result}

    # ---------------------- Helpers ----------------------
    @staticmethod
    def _map_score_to_severity(score: float, disorder: str) -> str:
        # Simple heuristic mapping based on total score ranges
        if score >= 20:
            return "severe"
        if score >= 15:
            return "moderately_severe"
        if score >= 10:
            return "moderate"
        if score >= 5:
            return "mild"
        return "minimal"

    @staticmethod
    def _meets_threshold(severity: str, disorder: str, text: str) -> bool:
        sev = (severity or "").lower()
        if disorder.lower() in {"suicidal_ideation", "suicidal thoughts", "suicidal-thoughts"}:
            # Any suicidality -> meets threshold
            return True
        return sev in {"moderate", "moderately_severe", "severe"}

    @staticmethod
    def _risk_from_context(disorder: str, severity: str, text: str) -> str:
        t = (text or "").lower()
        crisis_terms = ["suicide", "kill myself", "end my life", "die", "won't wake up", "plan", "intent"]
        if any(k in t for k in crisis_terms):
            return "immediate"
        if disorder.lower().startswith("suicid"):
            return "high"
        sev = (severity or "").lower()
        if sev in {"severe", "moderately_severe"}:
            return "high"
        if sev == "moderate":
            return "moderate"
        return "low"


