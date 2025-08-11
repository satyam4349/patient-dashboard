"""
AI Agent Service for Patient Companion Agent (PCA) and Clinical Assistant Agent (CAA).
Integrates with existing ML models and provides conversational AI capabilities.
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from dotenv import load_dotenv

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env
load_dotenv()


class PatientCompanionAgent:
    """
    Patient Companion Agent (PCA) for natural conversation-based journaling
    and emotional support.
    """
    
    def __init__(self):
        self.conversation_history = []
        self.user_context = {}
        
    async def process_message(self, user_id: str, message: str, context: Dict = None) -> Dict:
        """
        Process a message from the patient and generate an empathetic response.
        
        Args:
            user_id: Patient's user ID
            message: Patient's message
            context: Additional context (mood, recent entries, etc.)
            
        Returns:
            Dict with response and extracted insights
        """
        try:
            # TODO: Integrate with actual LLM (Google Gemini/GPT-4)
            # For now, provide rule-based responses
            
            message_lower = message.lower()
            
            # Crisis detection keywords
            crisis_keywords = ['suicide', 'kill myself', 'end it all', 'hurt myself', 'self-harm']
            if any(keyword in message_lower for keyword in crisis_keywords):
                return {
                    "status": "crisis_detected",
                    "response": "I'm really concerned about what you're sharing with me. Your safety is the most important thing right now. Please reach out to a crisis helpline immediately or contact your healthcare provider. You don't have to go through this alone.",
                    "crisis_level": "high",
                    "extracted_data": {
                        "crisis_indicators": True,
                        "mood_indicators": "severe_distress",
                        "requires_intervention": True
                    }
                }
            
            # Mood-related responses
            if any(word in message_lower for word in ['sad', 'depressed', 'down', 'low']):
                response = "I hear that you're feeling really down right now. That sounds really difficult. Can you tell me more about what's been contributing to these feelings? Sometimes talking through what's happening can help us understand it better."
                mood_indicator = "negative"
            elif any(word in message_lower for word in ['happy', 'good', 'great', 'better']):
                response = "It's wonderful to hear that you're feeling good! I'm really glad you're having a positive experience. What's been going well for you lately?"
                mood_indicator = "positive"
            elif any(word in message_lower for word in ['anxious', 'worried', 'stressed', 'nervous']):
                response = "It sounds like you're dealing with some anxiety right now. That can feel really overwhelming. What's been on your mind that's causing you to feel this way?"
                mood_indicator = "anxious"
            else:
                response = "Thank you for sharing that with me. I'm here to listen and support you. How are you feeling about everything you've shared?"
                mood_indicator = "neutral"
            
            # Extract insights from the conversation
            extracted_data = self._extract_insights(message, context or {})
            extracted_data["mood_indicator"] = mood_indicator
            
            return {
                "status": "success",
                "response": response,
                "extracted_data": extracted_data,
                "conversation_id": f"{user_id}_{datetime.now().timestamp()}"
            }
            
        except Exception as e:
            logger.error(f"PCA process_message error: {e}")
            return {
                "status": "error",
                "response": "I'm having trouble processing your message right now. Please try again in a moment.",
                "extracted_data": {}
            }
    
    def _extract_insights(self, message: str, context: Dict) -> Dict:
        """Extract clinical insights from the conversation."""
        insights = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_length": len(message),
            "word_count": len(message.split()),
            "themes": [],
            "emotions": [],
            "behaviors": [],
            "symptoms": []
        }
        
        message_lower = message.lower()
        
        # Theme detection
        if any(word in message_lower for word in ['work', 'job', 'boss', 'colleague']):
            insights["themes"].append("work_stress")
        if any(word in message_lower for word in ['family', 'parent', 'sibling', 'child']):
            insights["themes"].append("family_relationships")
        if any(word in message_lower for word in ['friend', 'social', 'party', 'people']):
            insights["themes"].append("social_relationships")
        if any(word in message_lower for word in ['sleep', 'tired', 'exhausted', 'insomnia']):
            insights["themes"].append("sleep_issues")
        
        # Emotion detection
        emotions = {
            'sadness': ['sad', 'depressed', 'down', 'blue', 'miserable'],
            'anxiety': ['anxious', 'worried', 'nervous', 'scared', 'panic'],
            'anger': ['angry', 'mad', 'furious', 'irritated', 'frustrated'],
            'joy': ['happy', 'joyful', 'excited', 'elated', 'cheerful'],
            'fear': ['afraid', 'terrified', 'frightened', 'scared']
        }
        
        for emotion, keywords in emotions.items():
            if any(keyword in message_lower for keyword in keywords):
                insights["emotions"].append(emotion)
        
        # Behavior indicators
        if any(word in message_lower for word in ['isolat', 'alone', 'withdraw']):
            insights["behaviors"].append("social_withdrawal")
        if any(word in message_lower for word in ['drink', 'alcohol', 'substance']):
            insights["behaviors"].append("substance_use")
        if any(word in message_lower for word in ['exercise', 'gym', 'run', 'walk']):
            insights["behaviors"].append("physical_activity")
        
        return insights


class ClinicalAssistantAgent:
    """
    Clinical Assistant Agent (CAA) for diagnostic support and clinical insights.
    """
    
    def __init__(self):
        self.knowledge_base = self._load_clinical_knowledge()
    
    def _load_clinical_knowledge(self) -> Dict:
        """Load clinical knowledge base (DSM-V criteria, treatment guidelines, etc.)"""
        # TODO: Load actual clinical knowledge base
        return {
            "dsm5_criteria": {
                "major_depressive_disorder": {
                    "criteria": [
                        "Depressed mood most of the day",
                        "Markedly diminished interest or pleasure",
                        "Significant weight loss or gain",
                        "Insomnia or hypersomnia",
                        "Psychomotor agitation or retardation",
                        "Fatigue or loss of energy",
                        "Feelings of worthlessness or guilt",
                        "Diminished ability to concentrate",
                        "Recurrent thoughts of death"
                    ],
                    "required_count": 5,
                    "duration": "2 weeks"
                },
                "generalized_anxiety_disorder": {
                    "criteria": [
                        "Excessive anxiety and worry",
                        "Difficulty controlling worry",
                        "Restlessness or feeling on edge",
                        "Being easily fatigued",
                        "Difficulty concentrating",
                        "Irritability",
                        "Muscle tension",
                        "Sleep disturbance"
                    ],
                    "required_count": 3,
                    "duration": "6 months"
                }
            }
        }
    
    async def analyze_patient_data(self, user_id: str, analysis_type: str = "comprehensive") -> Dict:
        """
        Analyze patient data and provide clinical insights.
        
        Args:
            user_id: Patient's user ID
            analysis_type: Type of analysis (comprehensive, risk_assessment, diagnostic)
            
        Returns:
            Dict with clinical analysis and recommendations
        """
        try:
            # TODO: Integrate with actual patient data from database
            # For now, provide mock analysis
            
            if analysis_type == "risk_assessment":
                return await self._perform_risk_assessment(user_id)
            elif analysis_type == "diagnostic":
                return await self._perform_diagnostic_analysis(user_id)
            else:
                return await self._perform_comprehensive_analysis(user_id)
                
        except Exception as e:
            logger.error(f"CAA analyze_patient_data error: {e}")
            return {
                "status": "error",
                "message": f"Analysis failed: {e}"
            }
    
    async def _perform_risk_assessment(self, user_id: str) -> Dict:
        """Perform risk assessment for the patient."""
        # TODO: Implement actual risk assessment using patient data
        return {
            "status": "success",
            "analysis_type": "risk_assessment",
            "risk_level": "medium",
            "risk_factors": [
                "Declining mood trends over past 2 weeks",
                "Reduced social activity mentions",
                "Sleep disturbance indicators"
            ],
            "protective_factors": [
                "Regular journal writing",
                "Mentions of support system",
                "Engagement with treatment"
            ],
            "recommendations": [
                "Increase monitoring frequency",
                "Consider medication review",
                "Schedule follow-up within 1 week"
            ],
            "confidence_score": 0.75
        }
    
    async def _perform_diagnostic_analysis(self, user_id: str) -> Dict:
        """Perform diagnostic analysis using DSM-V criteria."""
        # TODO: Implement actual diagnostic analysis
        return {
            "status": "success",
            "analysis_type": "diagnostic",
            "provisional_diagnoses": [
                {
                    "condition": "Major Depressive Disorder",
                    "criteria_met": 6,
                    "criteria_total": 9,
                    "confidence": 0.78,
                    "severity": "moderate",
                    "evidence": [
                        "Persistent depressed mood (14/14 days)",
                        "Anhedonia reported in 80% of entries",
                        "Sleep disturbance (avg 4.5 hours)",
                        "Fatigue mentioned daily",
                        "Concentration difficulties at work",
                        "Feelings of worthlessness (multiple entries)"
                    ]
                }
            ],
            "differential_diagnoses": [
                "Adjustment Disorder with Depressed Mood",
                "Persistent Depressive Disorder"
            ],
            "recommendations": [
                "Consider structured clinical interview",
                "Evaluate for medication management",
                "Assess suicide risk",
                "Consider CBT referral"
            ]
        }
    
    async def _perform_comprehensive_analysis(self, user_id: str) -> Dict:
        """Perform comprehensive patient analysis."""
        risk_assessment = await self._perform_risk_assessment(user_id)
        diagnostic_analysis = await self._perform_diagnostic_analysis(user_id)
        
        return {
            "status": "success",
            "analysis_type": "comprehensive",
            "patient_id": user_id,
            "analysis_date": datetime.now(timezone.utc).isoformat(),
            "risk_assessment": risk_assessment,
            "diagnostic_analysis": diagnostic_analysis,
            "treatment_recommendations": [
                "Continue current therapeutic approach",
                "Monitor mood trends closely",
                "Consider medication evaluation",
                "Increase session frequency if needed"
            ],
            "next_steps": [
                "Schedule follow-up in 1 week",
                "Review treatment plan",
                "Assess medication adherence",
                "Monitor for crisis indicators"
            ]
        }
    
    async def generate_clinical_summary(self, user_id: str, format_type: str = "soap") -> Dict:
        """Generate clinical summary in specified format."""
        try:
            analysis = await self.analyze_patient_data(user_id, "comprehensive")
            
            if format_type.lower() == "soap":
                return self._generate_soap_note(user_id, analysis)
            elif format_type.lower() == "progress":
                return self._generate_progress_note(user_id, analysis)
            else:
                return {"status": "error", "message": "Unsupported format type"}
                
        except Exception as e:
            logger.error(f"Generate clinical summary error: {e}")
            return {"status": "error", "message": f"Summary generation failed: {e}"}
    
    def _generate_soap_note(self, user_id: str, analysis: Dict) -> Dict:
        """Generate SOAP note format."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        soap_note = f"""# SOAP Note - Patient {user_id}
**Date**: {current_date}

## Subjective
Patient reports variable mood over the past week with continued engagement in daily journaling. Mood tracking shows average score of 3.2/5 with notable fluctuations. Patient describes ongoing challenges with sleep and concentration.

## Objective
- Mood entries: 7/7 days completed
- Journal entries: 6/7 days completed  
- Average mood score: 3.2/5
- Sleep pattern: Irregular, 4-6 hours nightly
- Engagement: Good therapeutic alliance maintained

## Assessment
{analysis.get('diagnostic_analysis', {}).get('provisional_diagnoses', [{}])[0].get('condition', 'Assessment pending')} - {analysis.get('diagnostic_analysis', {}).get('provisional_diagnoses', [{}])[0].get('severity', 'moderate')} severity
Risk level: {analysis.get('risk_assessment', {}).get('risk_level', 'medium')}

## Plan
- Continue current treatment approach
- Monitor mood trends weekly
- Review sleep hygiene strategies
- Follow-up in 1 week
- Crisis plan reviewed and updated
"""
        
        return {
            "status": "success",
            "format": "soap",
            "content": soap_note,
            "generated_date": current_date
        }
    
    def _generate_progress_note(self, user_id: str, analysis: Dict) -> Dict:
        """Generate progress note format."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        progress_note = f"""# Progress Note - Patient {user_id}
**Date**: {current_date}

## Treatment Summary
Patient continues in treatment with good engagement in digital therapeutic tools. Consistent use of mood tracking and journaling features demonstrates commitment to recovery process.

## Current Status
- **Mood Stability**: Moderate with some fluctuation
- **Functional Status**: Maintained with some impairment
- **Risk Level**: {analysis.get('risk_assessment', {}).get('risk_level', 'medium')}
- **Treatment Adherence**: Good

## Progress Indicators
- Journal completion rate: 85%
- Mood tracking compliance: 100%
- Therapeutic engagement: High

## Recommendations
{chr(10).join(f"- {rec}" for rec in analysis.get('treatment_recommendations', []))}

## Next Steps
{chr(10).join(f"- {step}" for step in analysis.get('next_steps', []))}
"""
        
        return {
            "status": "success",
            "format": "progress",
            "content": progress_note,
            "generated_date": current_date
        }


class AgentService:
    """Main service class for managing both AI agents."""
    
    def __init__(self):
        self.pca = PatientCompanionAgent()
        self.caa = ClinicalAssistantAgent()
    
    async def patient_chat(self, user_id: str, message: str, context: Dict = None) -> Dict:
        """Handle patient chat through PCA."""
        return await self.pca.process_message(user_id, message, context)
    
    async def clinical_analysis(self, user_id: str, analysis_type: str = "comprehensive") -> Dict:
        """Handle clinical analysis through CAA."""
        return await self.caa.analyze_patient_data(user_id, analysis_type)
    
    async def generate_report(self, user_id: str, report_type: str = "soap") -> Dict:
        """Generate clinical report through CAA."""
        return await self.caa.generate_clinical_summary(user_id, report_type)