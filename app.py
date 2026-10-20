from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os

app = Flask(__name__)

# Global cache for datasets and models
DATA_CACHE = {}
MODEL_CACHE = {}

def load_resources():
    """Load and cache datasets, ML model, and label encoders."""
    # 1. Load ML models and encoders
    try:
        if os.path.exists("model.pkl"):
            MODEL_CACHE["model"] = pickle.load(open("model.pkl", "rb"))
        if os.path.exists("college_encoder.pkl"):
            MODEL_CACHE["college_encoder"] = pickle.load(open("college_encoder.pkl", "rb"))
        if os.path.exists("branch_encoder.pkl"):
            MODEL_CACHE["branch_encoder"] = pickle.load(open("branch_encoder.pkl", "rb"))
        if os.path.exists("category_encoder.pkl"):
            MODEL_CACHE["category_encoder"] = pickle.load(open("category_encoder.pkl", "rb"))
        print("ML Models and Encoders loaded successfully.")
    except Exception as e:
        print(f"Warning loading ML resources: {e}")

    # 2. Load Datasets
    try:
        kcet_path = "data/kcet_cutoffs.csv"
        if os.path.exists(kcet_path):
            df_kcet = pd.read_csv(kcet_path)
            df_kcet["cutoff_rank"] = pd.to_numeric(df_kcet["cutoff_rank"], errors="coerce")
            DATA_CACHE["KCET"] = df_kcet
            print(f"KCET cutoffs loaded: {len(df_kcet):,} records.")

        jee_path = "data/jee_cutoffs.csv"
        if os.path.exists(jee_path):
            df_jee = pd.read_csv(jee_path)
            df_jee["cutoff_rank"] = pd.to_numeric(df_jee["cutoff_rank"], errors="coerce")
            DATA_CACHE["JEE"] = df_jee
            print(f"JEE cutoffs loaded: {len(df_jee):,} records.")
    except Exception as e:
        print(f"Error loading datasets: {e}")

# Pre-load resources on startup
load_resources()

def get_dataset(exam):
    """Retrieve cached dataset for KCET or JEE."""
    exam = exam.upper() if exam else "KCET"
    if exam not in DATA_CACHE:
        load_resources()
    return DATA_CACHE.get(exam, DATA_CACHE.get("KCET"))

def calculate_probability_and_tier(cutoff, rank):
    """
    Calculate admission probability percentage and tier:
    - Safe (Easy to Get): Cutoff >= 1.25 * Rank
    - Target (50-50 Chance): 0.85 * Rank <= Cutoff < 1.25 * Rank
    - Dream (Difficult to Get): Cutoff < 0.85 * Rank
    """
    if pd.isnull(cutoff) or cutoff <= 0:
        return "Unknown", 0, "unknown", 0

    rank = max(1, rank)
    ratio = cutoff / rank

    if ratio >= 1.25:
        tier = "Safe"
        badge_class = "tier-safe"
        prob = min(99, int(85 + min(14, (ratio - 1.25) * 10)))
    elif ratio >= 0.85:
        tier = "Target"
        badge_class = "tier-target"
        prob = int(50 + ((ratio - 0.85) / 0.40) * 34)
    else:
        tier = "Dream"
        badge_class = "tier-dream"
        prob = max(5, int((ratio / 0.85) * 45))

    diff = int(cutoff - rank)
    return tier, prob, badge_class, diff

@app.route("/", methods=["GET", "POST"])
def home():
    df_kcet = get_dataset("KCET")
    branches = sorted(df_kcet["branch"].dropna().unique().tolist()) if df_kcet is not None else []
    categories = sorted(df_kcet["category"].dropna().unique().tolist()) if df_kcet is not None else []
    regions = sorted(df_kcet["region"].dropna().unique().tolist()) if df_kcet is not None and "region" in df_kcet.columns else []
    districts = sorted(df_kcet["district"].dropna().unique().tolist()) if df_kcet is not None and "district" in df_kcet.columns else []

    if request.method == "POST":
        try:
            rank = int(request.form.get("rank", 10000))
        except ValueError:
            rank = 10000

        category = request.form.get("category", "GM").strip()
        branch = request.form.get("branch", "").strip()
        exam = request.form.get("exam", "KCET").strip().upper()
        region_filter = request.form.get("region", "All").strip()
        district_filter = request.form.get("district", "All").strip()
        quota_filter = request.form.get("quota", "All").strip()
        tier_filter = request.form.get("tier", "All").strip()

        data = get_dataset(exam)
        if data is None or data.empty:
            return "Dataset not found. Please verify data files exist.", 500

        filtered = data.copy()
        exam_districts = sorted(data["district"].dropna().unique().tolist()) if "district" in data.columns else []

        # Normalize category for JEE vs KCET
        cat_search = category
        if exam == "JEE":
            cat_upper = category.upper()
            if any(k in cat_upper for k in ["GENERAL", "GM", "OPEN", "CRL"]):
                cat_search = "General"
            elif "OBC" in cat_upper:
                cat_search = "OBC-NCL"
            elif "EWS" in cat_upper:
                cat_search = "EWS"
            elif "PWD" in cat_upper:
                cat_search = "PwD"
            elif "ST" in cat_upper:
                cat_search = "ST"
            elif "SC" in cat_upper:
                cat_search = "SC"

        # 1. Filter by Category
        if cat_search:
            if "category" in filtered.columns:
                cat_match = filtered["category"].astype(str).str.lower() == cat_search.lower()
                if not cat_match.any() and "base_category" in filtered.columns:
                    cat_match = filtered["base_category"].astype(str).str.lower() == cat_search.lower()
                if cat_match.any():
                    filtered = filtered[cat_match]

        # 2. Filter by Branch
        if branch and branch != "All Branches":
            exact_match = filtered["branch"].astype(str).str.lower() == branch.lower()
            if exact_match.any():
                filtered = filtered[exact_match]
            else:
                filtered = filtered[filtered["branch"].astype(str).str.contains(branch, case=False, na=False)]

        # 3. Filter by Region (General vs HK Quota)
        if region_filter and region_filter != "All" and "region" in filtered.columns:
            filtered = filtered[filtered["region"] == region_filter]

        # 4. Filter by Quota (General, Rural, Kannada)
        if quota_filter and quota_filter != "All" and "quota" in filtered.columns:
            filtered = filtered[filtered["quota"] == quota_filter]

        # 5. Filter by District / City Zone
        if district_filter and district_filter != "All" and "district" in filtered.columns:
            filtered = filtered[filtered["district"] == district_filter]

        # Deduplicate and sort by Cutoff Rank ascending (best colleges first)
        filtered = filtered.drop_duplicates(subset=["college", "branch", "category"])
        filtered = filtered.sort_values(by="cutoff_rank", ascending=True)

        # 6. Enrich records with Probability Tiers, Trends, and Badges
        results = []
        safe_colleges = []
        target_colleges = []
        dream_colleges = []

        for _, row in filtered.iterrows():
            cutoff = row["cutoff_rank"]
            tier, prob, badge_class, diff = calculate_probability_and_tier(cutoff, rank)

            item = {
                "college_id": row.get("college_id", ""),
                "college": row["college"],
                "branch": row["branch"],
                "category": row["category"],
                "quota": row.get("quota", "General"),
                "region": row.get("region", "General"),
                "district": row.get("district", "Other"),
                "cutoff_rank": int(cutoff) if pd.notnull(cutoff) else "N/A",
                "cutoff_2023": int(row["cutoff_2023"]) if pd.notnull(row.get("cutoff_2023")) else "—",
                "cutoff_2024": int(row["cutoff_2024"]) if pd.notnull(row.get("cutoff_2024")) else "—",
                "cutoff_2025": int(row["cutoff_2025"]) if pd.notnull(row.get("cutoff_2025")) else "—",
                "trend_pct": row.get("trend_pct", 0.0),
                "trend_label": row.get("trend_label", "Stable"),
                "tier": tier,
                "prob": prob,
                "badge_class": badge_class,
                "diff": diff,
                "diff_text": f"+{diff:,}" if diff > 0 else f"{diff:,}"
            }

            if tier == "Safe":
                safe_colleges.append(item)
            elif tier == "Target":
                target_colleges.append(item)
            elif tier == "Dream":
                dream_colleges.append(item)

            if tier_filter == "All" or tier_filter == tier:
                results.append(item)

        # AI Recommended (Balanced mix of Top Target & High-Quality Safe colleges)
        recommended = []
        if target_colleges:
            recommended.extend(target_colleges[:3])
        if safe_colleges:
            recommended.extend(safe_colleges[:2])
        if not recommended and results:
            recommended = results[:5]

        stats = {
            "total_matches": len(filtered),
            "safe_count": len(safe_colleges),
            "target_count": len(target_colleges),
            "dream_count": len(dream_colleges)
        }

        return render_template(
            "result.html",
            results=results,
            safe_colleges=safe_colleges,
            target_colleges=target_colleges,
            dream_colleges=dream_colleges,
            recommended=recommended,
            rank=rank,
            category=category,
            branch=branch if branch else "All Branches",
            exam=exam,
            region=region_filter,
            district=district_filter,
            districts=exam_districts,
            quota=quota_filter,
            tier_filter=tier_filter,
            stats=stats,
            branches=branches,
            categories=categories
        )

    return render_template(
        "index.html",
        branches=branches,
        categories=categories,
        regions=regions,
        districts=districts,
        total_colleges=len(df_kcet["college"].unique()) if df_kcet is not None else 460,
        total_records=len(df_kcet) if df_kcet is not None else 47116
    )

@app.route("/favourites")
def favourites():
    return render_template("favourites.html")

# JSON API Endpoints for dynamic client-side filtering / autocomplete
@app.route("/api/branches")
def api_branches():
    exam = request.args.get("exam", "KCET")
    df = get_dataset(exam)
    if df is not None and "branch" in df.columns:
        return jsonify(sorted(df["branch"].dropna().unique().tolist()))
    return jsonify([])

@app.route("/api/categories")
def api_categories():
    exam = request.args.get("exam", "KCET")
    df = get_dataset(exam)
    if df is not None and "category" in df.columns:
        return jsonify(sorted(df["category"].dropna().unique().tolist()))
    return jsonify([])

@app.route("/api/districts")
def api_districts():
    exam = request.args.get("exam", "KCET")
    df = get_dataset(exam)
    if df is not None and "district" in df.columns:
        return jsonify(sorted(df["district"].dropna().unique().tolist()))
    return jsonify([])

@app.route("/api/colleges")
def api_colleges():
    exam = request.args.get("exam", "KCET")
    df = get_dataset(exam)
    if df is not None:
        cols = df[["college_id", "college"]].drop_duplicates().to_dict(orient="records")
        return jsonify(cols)
    return jsonify([])

if __name__ == "__main__":
    app.run(debug=True, port=5000)