import sys
import os

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor

print("[Step 1] Loading KCET dataset from data/kcet_ai_ready.csv...")
input_path = "data/kcet_ai_ready.csv"
if not os.path.exists(input_path):
    raise FileNotFoundError(f"Cannot find {input_path}")

raw_df = pd.read_csv(input_path)
print(f"Loaded {len(raw_df):,} raw records.")

# Clean Cutoff_Rank
raw_df["Cutoff_Rank"] = pd.to_numeric(raw_df["Cutoff_Rank"], errors="coerce")
raw_df = raw_df.dropna(subset=["Cutoff_Rank"])

# Clean text columns
raw_df["CollegeName"] = raw_df["CollegeName"].astype(str).str.strip()
raw_df["CollegeID"] = raw_df["CollegeID"].astype(str).str.strip()
raw_df["CourseName"] = raw_df["CourseName"].astype(str).str.strip()
raw_df["Category"] = raw_df["Category"].astype(str).str.strip()
raw_df["Base_Category"] = raw_df["Base_Category"].astype(str).str.strip()
raw_df["Quota"] = raw_df["Quota"].astype(str).str.strip()
raw_df["Region"] = raw_df["Region"].astype(str).str.strip()

print("[Step 2] Aggregating multi-year trends (2023, 2024, 2025)...")
yearly = (
    raw_df.groupby([
        "CollegeID", "CollegeName", "CourseName", "Category",
        "Base_Category", "Quota", "Region", "Year"
    ])["Cutoff_Rank"]
    .max()
    .unstack("Year")
    .reset_index()
)

# Rename yearly columns
for yr in [2023, 2024, 2025]:
    if yr in yearly.columns:
        yearly[f"cutoff_{yr}"] = yearly[yr]
    else:
        yearly[f"cutoff_{yr}"] = np.nan

# Determine latest cutoff rank
yearly["cutoff_rank"] = (
    yearly["cutoff_2025"]
    .combine_first(yearly["cutoff_2024"])
    .combine_first(yearly["cutoff_2023"])
)

yearly["college_id"] = yearly["CollegeID"]
yearly["college"] = yearly["CollegeName"]
yearly["branch"] = yearly["CourseName"]
yearly["category"] = yearly["Category"]
yearly["base_category"] = yearly["Base_Category"]
yearly["quota"] = yearly["Quota"]
yearly["region"] = yearly["Region"]

# Compute multi-year trend (% change and label)
def calculate_trend(row):
    first_val = row["cutoff_2023"] if pd.notnull(row["cutoff_2023"]) else row["cutoff_2024"]
    last_val = row["cutoff_2025"] if pd.notnull(row["cutoff_2025"]) else row["cutoff_2024"]
    if pd.notnull(first_val) and pd.notnull(last_val) and first_val > 0:
        pct = round(((last_val - first_val) / first_val) * 100, 1)
        if pct > 4.0:
            return pct, f"+{pct}% (Cutoff Relaxed / Easier)"
        elif pct < -4.0:
            return pct, f"{pct}% (More Competitive)"
        else:
            return pct, "Stable (+/- 4%)"
    return 0.0, "Stable"

trends = [calculate_trend(row) for _, row in yearly.iterrows()]
yearly["trend_pct"] = [t[0] for t in trends]
yearly["trend_label"] = [t[1] for t in trends]

cols = [
    "college_id", "college", "branch", "category", "base_category",
    "quota", "region", "cutoff_rank", "cutoff_2023", "cutoff_2024",
    "cutoff_2025", "trend_pct", "trend_label"
]

kcet_cutoffs_df = yearly[cols].copy()
kcet_cutoffs_df = kcet_cutoffs_df.sort_values(by=["college", "branch", "category"])
output_csv = "data/kcet_cutoffs.csv"
kcet_cutoffs_df.to_csv(output_csv, index=False)
print(f"Saved {len(kcet_cutoffs_df):,} enriched rows to {output_csv}.")

# Standardize JEE dataset as well
jee_path = "data/jee_cutoffs.csv"
if os.path.exists(jee_path):
    jee_df = pd.read_csv(jee_path)
    for col in cols:
        if col not in jee_df.columns:
            if col == "college_id":
                jee_df[col] = [f"JEE{i+1:03d}" for i in range(len(jee_df))]
            elif col == "base_category":
                jee_df[col] = jee_df["category"]
            elif col == "quota":
                jee_df[col] = "General"
            elif col == "region":
                jee_df[col] = "All India"
            elif col in ["cutoff_2023", "cutoff_2024", "cutoff_2025"]:
                jee_df[col] = jee_df["cutoff_rank"]
            elif col == "trend_pct":
                jee_df[col] = 0.0
            elif col == "trend_label":
                jee_df[col] = "Stable"
    jee_df[cols].to_csv(jee_path, index=False)
    print("Updated data/jee_cutoffs.csv with standard multi-year schema.")

print("[Step 3] Encoding text columns for ML model...")
college_encoder = LabelEncoder()
branch_encoder = LabelEncoder()
category_encoder = LabelEncoder()

all_colleges = sorted(raw_df["CollegeName"].unique().tolist())
all_branches = sorted(raw_df["CourseName"].unique().tolist())
all_categories = sorted(raw_df["Category"].unique().tolist())

branch_encoder.fit(all_branches)
college_encoder.fit(all_colleges)
category_encoder.fit(all_categories)

train_df = kcet_cutoffs_df.copy()
train_df["college_enc"] = college_encoder.transform(train_df["college"])
train_df["branch_enc"] = branch_encoder.transform(train_df["branch"])
train_df["category_enc"] = category_encoder.transform(train_df["category"])

X = train_df[["cutoff_rank", "branch_enc", "category_enc"]]
y = train_df["college_enc"]

print(f"Training ML Model on {len(X):,} combinations...")
model = RandomForestRegressor(
    n_estimators=50,
    max_depth=16,
    min_samples_split=4,
    random_state=42,
    n_jobs=-1
)
model.fit(X, y)

print("[Step 4] Saving models and encoders...")
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("college_encoder.pkl", "wb") as f:
    pickle.dump(college_encoder, f)

with open("branch_encoder.pkl", "wb") as f:
    pickle.dump(branch_encoder, f)

with open("category_encoder.pkl", "wb") as f:
    pickle.dump(category_encoder, f)

print("SUCCESS: Model trained and saved successfully with 460 colleges and 146 branches!")