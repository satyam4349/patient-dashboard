import pandas as pd
import os
from sentence_transformers import SentenceTransformer

# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the existing mock data CSV
csv_path = os.path.join(current_dir, "mock_data", "mock_user_journal_data.csv")
df = pd.read_csv(csv_path)

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Generate embeddings for journal entries
embeddings = embedder.encode(df["journal_entry"].astype(str).tolist(), convert_to_numpy=True, show_progress_bar=True)

# Store as comma-separated strings in the CSV
df["journal_entry_embedding"] = [",".join(map(str, vec)) for vec in embeddings]

# Map disorder predictions to risk levels
def map_disorder_to_risk_level(disorder_prediction):
    if pd.isna(disorder_prediction) or disorder_prediction == "None":
        return "low"
    elif disorder_prediction in ["Mild Anxiety"]:
        return "low"
    elif disorder_prediction in ["Depression", "Anxiety"]:
        return "moderate"
    elif disorder_prediction in ["Schizophrenia"]:
        return "high"
    elif disorder_prediction in ["Suicidal Ideation"]:
        return "immediate"
    else:
        return "moderate"  # default

# Add risk level column
df["risk_level"] = df["disorder_prediction"].apply(map_disorder_to_risk_level)

# Create balanced test set (low/moderate/high/immediate)
available_levels = df["risk_level"].unique()
balanced_dfs = []
for level in ["low", "moderate", "high", "immediate"]:
    if level in available_levels:
        level_df = df[df["risk_level"] == level]
        sample_size = min(5, len(level_df))
        if sample_size > 0:
            balanced_dfs.append(level_df.sample(sample_size, random_state=42))

if balanced_dfs:
    balanced_df = pd.concat(balanced_dfs).reset_index(drop=True)
else:
    balanced_df = df.copy()  # fallback to all data

# Save with proper paths
output_path_full = os.path.join(current_dir, "mock_data", "mock_user_journal_data_with_embeddings.csv")
output_path_balanced = os.path.join(current_dir, "mock_data", "mock_user_journal_balanced_test_with_embeddings.csv")

df.to_csv(output_path_full, index=False)
balanced_df.to_csv(output_path_balanced, index=False)

print(f"✅ Saved: {output_path_full}")
print(f"✅ Saved: {output_path_balanced}")
print(f"📊 Total entries: {len(df)}")
print(f"📊 Balanced test entries: {len(balanced_df)}")
print(f"📊 Risk level distribution in balanced set:")
if len(balanced_df) > 0:
    print(balanced_df["risk_level"].value_counts().to_string())
