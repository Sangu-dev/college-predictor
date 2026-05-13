import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import pickle

# Load dataset
df = pd.read_csv("data/kcet_cutoffs.csv")
print(df["category"].unique())

# Remove missing values
df = df.dropna()

# Encode text columns
college_encoder = LabelEncoder()
branch_encoder = LabelEncoder()
category_encoder = LabelEncoder()

df["college"] = college_encoder.fit_transform(df["college"])
df["branch"] = branch_encoder.fit_transform(df["branch"])
df["category"] = category_encoder.fit_transform(df["category"])

# Features and target
X = df[["cutoff_rank", "branch", "category"]]
y = df["college"]

# Train model
model = RandomForestRegressor(n_estimators=100)

model.fit(X, y)

# Save model
pickle.dump(model, open("model.pkl", "wb"))

# Save encoders
pickle.dump(college_encoder, open("college_encoder.pkl", "wb"))
pickle.dump(branch_encoder, open("branch_encoder.pkl", "wb"))
pickle.dump(category_encoder, open("category_encoder.pkl", "wb"))

print("Model trained successfully!")