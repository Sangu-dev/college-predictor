from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
import sys

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


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

def classify_college_and_fees(name, exam="KCET", college_id=""):
    """
    Classify institution type, updated KEA/JoSAA CET fee range, affiliation, and fee details.
    Uses latest KEA Government Orders & KUPECA consensual agreement updates (2024-2025).
    """
    exam = str(exam).upper() if exam else "KCET"
    n = str(name).upper()
    cid = str(college_id).upper()

    if exam == "JEE" or "NIT" in n or "NATIONAL INSTITUTE OF TECHNOLOGY" in n:
        return {
            "type": "National Institute of Technology",
            "type_short": "Central Govt (NIT)",
            "fee_range": "₹1,25,000 – ₹1,50,000 / yr",
            "fee_notes": "JoSAA central tuition fee structure. 100% waiver for SC/ST/PwD & family income < ₹1L; 66% waiver for income ₹1L–₹5L.",
            "affiliation": "Institute of National Importance (Autonomous)",
            "governance_desc": "Centrally funded premier technical institution governed by the Council of NITs under Ministry of Education, Govt. of India.",
            "accreditation_note": "Autonomous Central Degree Granting",
            "icon": "🏛️",
            "snq_fee": "🛡️ 100% Tuition Waiver: Family Income < ₹1L (JoSAA)",
            "badge_class": "badge-govt"
        }

    # 1. Government Engineering Colleges
    govt_keywords = [
        "GOVERNMENT", "GOVT", "GEC", "UNIVERSITY OF VISVESVARAYA", "UVCE", 
        "S.K.S.J.T", "SKSJT", "KARNATAKA INSTITUTE OF APPLIED TECHNOLOGY"
    ]
    if any(k in n for k in govt_keywords):
        return {
            "type": "Government Engineering College",
            "type_short": "Government (KEA Quota)",
            "fee_range": "₹40,860 – ₹45,750 / yr",
            "fee_notes": "Official KEA Govt fee (~₹24k tuition + VTU/univ registration). SC/ST (<₹2.5L) pay ₹21,360.",
            "affiliation": "Constituent / State Govt University",
            "governance_desc": "State Government institution operating under Karnataka Directorate of Technical Education with statutory subsidized fee scales.",
            "accreditation_note": "State Government Constituent",
            "icon": "🏛️",
            "snq_fee": "🛡️ SNQ Supernumerary Quota: ₹21,360 / yr",
            "badge_class": "badge-govt"
        }

    # 2. Private Aided & Autonomous Institutions
    aided_auto_keywords = [
        "R.V. COLLEGE", "RV COLLEGE", "B.M.S. COLLEGE OF ENGINEERING", "BMS COLLEGE OF ENGINEERING",
        "RAMAIAH INSTITUTE OF TECHNOLOGY", "M S RAMAIAH", "M.S. RAMAIAH", "NATIONAL INSTITUTE OF ENGINEERING",
        "SRI JAYACHAMARAJENDRA", "SJCE", "JSS SCIENCE AND TECHNOLOGY", "SIDDAGANGA INSTITUTE",
        "P.E.S. COLLEGE OF ENGINEERING, MANDYA", "PES COLLEGE OF ENGINEERING MANDYA",
        "DR. AMBEDKAR INSTITUTE OF TECHNOLOGY", "DAYANANDA SAGAR COLLEGE OF ENGINEERING",
        "BANGALORE INSTITUTE OF TECHNOLOGY", "NMAM INSTITUTE", "KLE TECH", "B.V. BHOOMARADDI",
        "SDM COLLEGE OF ENGINEERING", "BASAVESHWAR ENGINEERING", "MALNAD COLLEGE",
        "B N M INSTITUTE", "BNM INSTITUTE", "NITTE MEENAKSHI", "NEW HORIZON COLLEGE OF ENGINEERING",
        "CMR INSTITUTE OF TECHNOLOGY", "R N S INSTITUTE", "RNS INSTITUTE",
        "SIR M VISVESVARAYA INSTITUTE", "GOGTE INSTITUTE", "POOJYA DODDAPPA APPA", "PDA COLLEGE",
        "THE OXFORD COLLEGE OF ENGINEERING", "JSS ACADEMY OF TECHNICAL EDUCATION"
    ]
    if any(k in n for k in aided_auto_keywords):
        return {
            "type": "Private Aided / Autonomous",
            "type_short": "Aided / Autonomous (VTU)",
            "fee_range": "₹40,860 (Aided) / ₹1,06,230 – ₹1,15,000 (Unaided)",
            "fee_notes": "Aided seats: ₹40,860/yr; Unaided autonomous seats: ~₹1.15L/yr (KEA quota).",
            "affiliation": "Autonomous under VTU",
            "governance_desc": "Autonomous academic freedom allowing modern industry curricula and in-house continuous assessments; degree conferred by VTU.",
            "accreditation_note": "Autonomous Institution (VTU)",
            "icon": "🏢",
            "snq_fee": "🛡️ SNQ Quota: ₹21,360 (Aided) / ₹31,360 (Unaided)",
            "badge_class": "badge-aided"
        }

    # 3. State Private / Deemed Universities
    deemed_keywords = [
        "PES UNIVERSITY", "REVA UNIVERSITY", "PRESIDENCY UNIVERSITY", "ALLIANCE UNIVERSITY",
        "AMITY UNIVERSITY", "DAYANANDA SAGAR UNIVERSITY", "CMR UNIVERSITY", "GITAM", "GARDEN CITY"
    ]
    if any(k in n for k in deemed_keywords):
        return {
            "type": "State Private / Deemed University",
            "type_short": "Private University (Deemed)",
            "fee_range": "₹1,06,230 – ₹1,15,000 / yr",
            "fee_notes": "Official KEA CET allotment quota. Total with university charges: ~₹1.25L – ₹1.35L/yr.",
            "affiliation": "State Private University (Deemed)",
            "governance_desc": "Recognized State Private University with unitary campus status, independent syllabus, credit-based grading, and degree-awarding powers.",
            "accreditation_note": "Unitary Private University",
            "icon": "🏫",
            "snq_fee": "🛡️ SNQ Supernumerary Quota: ₹31,360 / yr",
            "badge_class": "badge-private"
        }

    # 4. Standard Private Unaided (VTU Affiliated)
    return {
        "type": "Private Unaided Engineering College",
        "type_short": "Private Unaided (VTU)",
        "fee_range": "₹1,06,230 – ₹1,14,690 / yr",
        "fee_notes": "Updated KEA-KUPECA fee scale. Total with college lab/misc fees: ~₹1.15L – ₹1.25L/yr.",
        "affiliation": "VTU Affiliated (Non-Autonomous)",
        "governance_desc": "Affiliated with Visvesvaraya Technological University (VTU), Belagavi. Follows standardized state-wide syllabus and central university examinations.",
        "accreditation_note": "VTU Affiliated College",
        "icon": "🏫",
        "snq_fee": "🛡️ SNQ Supernumerary Quota: ₹31,360 / yr",
        "badge_class": "badge-private"
    }

def calculate_round_breakdown(cutoff, rank, exam="KCET"):
    """
    Calculate Round 1, Round 2, and Extended Round cutoffs along with candidate round status.
    Round 1 is strictest (~90% of final cutoff).
    Round 2 is standard allotment (~98% of final cutoff).
    Extended Round relaxes up to +8-10% (~108% of cutoff).
    """
    exam = str(exam).upper() if exam else "KCET"
    is_jee = (exam == "JEE")

    r1_title = "JoSAA Round 1" if is_jee else "KEA Round 1"
    r2_title = "JoSAA Final Round" if is_jee else "KEA Round 2"
    rext_title = "CSAB Special Round" if is_jee else "2nd Extended Round"
    progression_title = "JoSAA & CSAB Seat Allotment Progression" if is_jee else "Round-by-Round Seat Allotment"
    authority_label = "Official JoSAA / CSAB System" if is_jee else "Official KEA Counseling System"
    strategy_tip = (
        "CSAB Special Rounds frequently see significant rank relaxation as top candidates confirm IITs or BITS Pilani seats."
        if is_jee else
        "Cutoffs typically relax by 8% to 12% in the Second Extended Round as candidates surrender seats to join central or medical quotas."
    )

    if pd.isnull(cutoff) or cutoff <= 0:
        return {
            "r1": "—", "r2": "—", "rext": "—",
            "r1_num": 0, "r2_num": 0, "rext_num": 0,
            "r1_status": "Unknown", "r2_status": "Unknown", "rext_status": "Unknown",
            "likely_round": "Unknown",
            "r1_title": r1_title, "r2_title": r2_title, "rext_title": rext_title,
            "progression_title": progression_title, "authority_label": authority_label,
            "strategy_tip": strategy_tip
        }

    c = float(cutoff)
    r1 = max(1, int(round(c * 0.90)))
    r2 = max(1, int(round(c * 0.98)))
    rext = max(1, int(round(c * 1.08)))

    r = float(rank) if rank and rank > 0 else 0

    if r > 0:
        if r <= r1:
            r1_status = "Likely Allotted"
            r2_status = "Safe Confirmed"
            rext_status = "Safe Confirmed"
            likely_round = "Round 1 (Immediate Allotment)"
        elif r <= r2:
            r1_status = "Wait for Upgrade"
            r2_status = "Likely Allotted"
            rext_status = "Safe Confirmed"
            likely_round = "Round 2 (High Probability)"
        elif r <= rext:
            r1_status = "Unlikely in R1"
            r2_status = "Borderline in R2"
            rext_status = "Likely in Extended Round"
            likely_round = "Extended / CSAB Round (Vacancy Seat)"
        else:
            r1_status = "Low Chance"
            r2_status = "Low Chance"
            rext_status = "Reach Choice"
            likely_round = "Reach Choice (Special Round)"
    else:
        r1_status = "N/A"
        r2_status = "N/A"
        rext_status = "N/A"
        likely_round = "Enter rank"

    return {
        "r1": f"{r1:,}",
        "r2": f"{r2:,}",
        "rext": f"{rext:,}",
        "r1_num": r1,
        "r2_num": r2,
        "rext_num": rext,
        "r1_status": r1_status,
        "r2_status": r2_status,
        "rext_status": rext_status,
        "likely_round": likely_round,
        "r1_title": r1_title,
        "r2_title": r2_title,
        "rext_title": rext_title,
        "progression_title": progression_title,
        "authority_label": authority_label,
        "strategy_tip": strategy_tip
    }

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
            meta = classify_college_and_fees(row["college"], exam, row.get("college_id", ""))
            rounds = calculate_round_breakdown(cutoff, rank, exam)

            raw_dist = str(row.get("district", "Other"))
            clean_dist = raw_dist.split("(")[0].strip() if "(" in raw_dist else raw_dist
            if not clean_dist or clean_dist.lower() == "nan":
                clean_dist = "Other"

            item = {
                "college_id": row.get("college_id", ""),
                "college": row["college"],
                "branch": row["branch"],
                "category": row["category"],
                "quota": row.get("quota", "General"),
                "region": row.get("region", "General"),
                "district": clean_dist,
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
                "diff_text": f"+{diff:,}" if diff > 0 else f"{diff:,}",
                "college_type": meta.get("type", "Engineering College"),
                "college_type_short": meta.get("type_short", "Private (KEA Quota)"),
                "fee_range": meta.get("fee_range", "KEA Regulated Quota"),
                "fee_notes": meta.get("fee_notes", "Statutory regulated fee."),
                "affiliation": meta.get("affiliation", "VTU Affiliated"),
                "governance_desc": meta.get("governance_desc", "Academic institution."),
                "accreditation_note": meta.get("accreditation_note", "Accredited Program"),
                "fee_icon": meta.get("icon", "🏛️"),
                "snq_fee": meta.get("snq_fee", "SNQ: ₹31,360 / yr"),
                "fee_badge_class": meta.get("badge_class", "badge-private"),
                "round_1": rounds["r1"],
                "round_2": rounds["r2"],
                "round_ext": rounds["rext"],
                "round_1_status": rounds["r1_status"],
                "round_2_status": rounds["r2_status"],
                "round_ext_status": rounds["rext_status"],
                "likely_round": rounds["likely_round"],
                "round_1_title": rounds.get("r1_title", "Round 1"),
                "round_2_title": rounds.get("r2_title", "Round 2"),
                "round_ext_title": rounds.get("rext_title", "Extended Round"),
                "progression_title": rounds.get("progression_title", "Round-by-Round Seat Allotment"),
                "authority_label": rounds.get("authority_label", "Official Counseling System"),
                "strategy_tip": rounds.get("strategy_tip", "")
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

@app.route("/api/college_details")
def api_college_details():
    name = request.args.get("college", "")
    exam = request.args.get("exam", "KCET")
    cid = request.args.get("college_id", "")
    cutoff = request.args.get("cutoff", 0)
    rank = request.args.get("rank", 0)
    try:
        cutoff = float(cutoff)
    except:
        cutoff = 0.0
    try:
        rank = float(rank)
    except:
        rank = 0.0

    meta = classify_college_and_fees(name, exam, cid)
    rounds = calculate_round_breakdown(cutoff, rank, exam)
    tier, prob, badge_class, diff = calculate_probability_and_tier(cutoff, rank)

    return jsonify({
        "college": name,
        "college_id": cid,
        "exam": exam,
        "metadata": meta,
        "rounds": rounds,
        "tier": tier,
        "prob": prob,
        "diff": diff
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)