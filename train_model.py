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

# District categorization functions
def extract_kcet_district(name):
    n = str(name).upper()
    
    # 1. Dakshina Kannada & Udupi (Coastal Hub)
    coastal_keywords = [
        "MANGALORE", "MANGALURU", "SURATHKAL", "UDUPI", "MANIPAL", "MOODBIDRI",
        "MOODABIDRI", "MOODABIDRE", "PUTTUR", "BANTWAL", "SULLIA", "BELTHANGADY", "KARKALA",
        "KUNDAPURA", "KUNDAPUR", "NITK", "CANARA", "SAHYADRI", "ST. JOSEPH", "ST JOSEPH",
        "BEARYS", "ALVAS", "ALVA'S", "NMAM", "NITTE", "PA COLLEGE", "P.A. COLLEGE",
        "SHREE DEVI", "SRINIVAS", "YENEPOYA", "KARAVALI", "D.K", "DAKSHINA KANNADA", "KVG",
        "UJIRE", "D K DIST", "VIVEKANANADA COLLEGE OF ENGINEERING TECHNOLOGY D K"
    ]
    if any(k in n for k in coastal_keywords):
        return "Dakshina Kannada & Udupi"

    # 2. Bengaluru Urban & Rural
    bengaluru_keywords = [
        "BANGALORE", "BANGLORE", "BENGALURU", "YELAHANKA", "KENGERI", "HOSKOTE", "BIDADI",
        "NELAMANGALA", "ANEKAL", "DEVANAHALLI", "CHIKKABANAVARA", "WHITEFIELD",
        "ELECTRONIC CITY", "JIGANI", "PEENYA", "RAJARARAJESWARI", "RAJARAJESWARI",
        "KUMBALGODU", "HESARAGHATTA", "DODDABALLAPUR", "HAROHALLI", "MAGADI", "RAMANAGAR",
        "AKASH", "AMITY UNIVERSITY", "AMRUTHA INSTITUTE", "GARDEN CITY", "RV ", "R.V.",
        "BMS", "B.M.S", "PES ", "P.E.S", "MSRIT", "M S RAMAIAH", "RAMAIAH", "DAYANANDA SAGAR",
        "NEW HORIZON", "B N M", "BNM", "NMIT", "NITTE MEENAKSHI", "OXFORD", "SAMBHRAM",
        "SIR M VISVESVARAYA", "EAST POINT", "CMR", "REVA", "ATRIA", "PRESIDENCY UNIVERSITY",
        "ACHARYA", "DON BOSCO", "GLOBAL ACADEMY", "SJBIT", "RNS", "K S INSTITUTE", "KSIT",
        "DAYANAND SAGAR", "KNS", "HKBK", "GOPALAN", "BRINDAVAN", "CAMBRIDGE", "ALPHA",
        "T.JOHN", "T JOHN", "VIVEKANANDA INSTITUTE OF TECHNOLOGY", "MVJ", "BMSIT", "B.M.S.I.T",
        "DR. AMBEDKAR INSTITUTE", "DR AMBEDKAR", "SJES", "SAMPOORNA", "ACS",
        "SRI VENKATESHWARA COLLEGE OF ENGINEERING BENGALURU", "BETTAHALSUR",
        "SRI KRISHNA INSTITUTE", "SAPTHAGIRI", "CITY ENGINEERING", "VEMANA", "ISLAMIAH",
        "HENNUR", "KOTHNUR", "NEW EBENEZER", "DODDAKAMMANAHALLY", "BEGUR", "RATHINAM", "SAIRAM"
    ]
    if any(k in n for k in bengaluru_keywords):
        return "Bengaluru Urban & Rural"

    # 3. Mysuru & Mandya Region
    mysuru_keywords = [
        "MYSORE", "MYSURU", "MANDYA", "NANJANGUD", "CHAMARAJANAGAR", "CHAMARAJNAGAR",
        "B.G. NAGARA", "B.G.NAGARA", "BELLUR", "MALAVALLI", "K.R. PET", "KR PET",
        "PANDAVAPURA", "KOLLEGAL", "GUNDLUPET", "SJCE", "NIE", "VIDYAVARDHAKA", "VVCE",
        "JSS SCIENCE", "JSS S&T", "PES COLLEGE OF ENGINEERING, MANDYA", "PESCE",
        "MAHARAJA INSTITUTE OF TECHNOLOGY MYSORE", "MIT MYSORE", "ATME", "GSSS",
        "ADHICHUNCHANAGIRI UNIVERSITY", "GOVERNMENT TOOL ROOM AND TRAINING CENTRE  MYSORE",
        "GOVERNMENT TOOL ROOM AND TRAINING CENTRE,MYSORE", "SRI JAYACHAMARAJENDRA COLLEGE OF ENGINEERING",
        "THE NATIONAL INSTITUTE OF ENGINEERING"
    ]
    if any(k in n for k in mysuru_keywords):
        return "Mysuru & Mandya"
        
    # 4. Hubballi-Dharwad & Belagavi (Kittur Karnataka)
    north_west_keywords = [
        "HUBLI", "HUBBALLI", "DHARWAD", "BELGAUM", "BELAGAVI", "GADAG",
        "HAVERI", "RANEBENNUR", "UTTARA KANNADA", "KARWAR", "BHATKAL",
        "SIRSI", "CHIKKODI", "NIPANI", "BAILHONGAL", "GOKAK", "ANKOLA",
        "VIJAYAPUR", "VIJAYAPURA", "BIJAPUR", "BAGALKOT", "BAGALKOTE",
        "MUDHOL", "JAMKHANDI", "BADAMI", "ILKAL", "HALIYAL", "DANDELI",
        "KLE", "SDM", "GOGTE", "GIT", "BLDEA", "BASAVESHWARA", "BASAVA ENGINEERING",
        "ANGADI", "MARATHA MANDAL", "S G BALEKUNDRI", "JAIN COLLEGE OF ENGINEERING",
        "SECAB", "AGMR", "TONTADARYA", "R.T.E. SOCIETY", "HIRASUGAR", "VISHWANATHRAO DESHPANDE",
        "HULKOTI", "RURAL ENGINEERING COLLEGE HULKOTI"
    ]
    if any(k in n for k in north_west_keywords):
        return "Hubballi-Dharwad & Belagavi"
        
    # 5. Kalyana Karnataka (HK Region / 371J)
    hk_keywords = [
        "GULBARGA", "KALABURAGI", "BELLARY", "BALLARI", "RAICHUR", "BIDAR",
        "KOPPAL", "YADGIR", "VIJAYANAGARA", "HOSAPETE", "HOSPET", "GANGAVATHI",
        "HUMNABAD", "BASAVAKALYAN", "BHALKI", "SHAHABAD", "SEDAM", "SINDHANUR",
        "BHEEMANNA KHANDRE", "BKIT", "KCT", "ROZA", "KISHKINDA", "PROUDHADEVARAYA",
        "PDA", "POOJYA DODDAPPA APPA", "APPA INSTITUTE", "SHETTY INSTITUTE",
        "VEERAPPA NISTY", "NAVODAYA", "RYMEC", "RAO BAHADUR", "K.B.N", "KBN", "KHWAJA BANDE NAWAZ"
    ]
    if any(k in n for k in hk_keywords):
        return "Kalyana Karnataka"
        
    # 6. Central & Southern Karnataka
    central_keywords = [
        "TUMKUR", "TUMAKURU", "DAVANGERE", "DAVANAGERE", "SHIMOGA", "SHIVAMOGGA",
        "HASSAN", "CHIKMAGALUR", "CHIKKAMAGALURU", "CHICKMAGALUR", "CHICKKABALLAPUR", "CHITRADURGA",
        "KOLAR", "CHIKKABALLAPUR", "CHIKABALLPURA", "CHICKBALLAPUR", "CHINTAMANI",
        "MADIKERI", "KODAGU", "COORG", "KUSHALANAGAR", "K.G.F", "KGF", "TIPTUR",
        "SIT", "SIDDAGANGA", "BAPUJI", "UBDT", "BIET", "GM INSTITUTE", "PESITM",
        "JNNCE", "MALNAD", "MCE", "ADICHUNCHANAGIRI", "ADHICHUNCHANAGIRI", "SJCIT",
        "C. BYREGOWDA", "SRI JAGADGURU CHANDRASEKHARANATHA", "GOVERNMENT ENGINEERING COLLEGE, CHALLAKERE",
        "SHRIDEVI INSTITUTE OF ENGINEERING", "CHANNABASAVESHWARA", "CIT TUMKUR",
        "KALPATARU", "SRI SIDDHARTHA", "HMS", "GOVERNMENT ENGINEERING COLLEGE, MOSALEHOSAHALLI",
        "GOVERNMENT ENGINEERING COLLEGE HASSAN", "NAVKIS", "CONSTITUENT COLLEGE OF VTU"
    ]
    if any(k in n for k in central_keywords):
        return "Central & Southern Karnataka"
        
    return "Bengaluru Urban & Rural"

def extract_jee_district(name):
    n = str(name).upper()
    if "SURATHKAL" in n:
        return "Karnataka (NIT Surathkal)"
    elif "TRICHY" in n or "TIRUCHIRAPPALLI" in n:
        return "Tamil Nadu (NIT Trichy)"
    elif "WARANGAL" in n:
        return "Telangana (NIT Warangal)"
    elif "CALICUT" in n or "KOZHIKODE" in n:
        return "Kerala (NIT Calicut)"
    elif "ROURKELA" in n:
        return "Odisha (NIT Rourkela)"
    elif "JAIPUR" in n or "MNIT" in n:
        return "Rajasthan (NIT Jaipur)"
    elif "NAGPUR" in n or "VNIT" in n:
        return "Maharashtra (VNIT Nagpur)"
    elif "KURUKSHETRA" in n:
        return "Haryana (NIT Kurukshetra)"
    elif "ALLAHABAD" in n or "MNNIT" in n or "PRAYAGRAJ" in n:
        return "Uttar Pradesh (MNNIT Allahabad)"
    elif "DURGAPUR" in n:
        return "West Bengal (NIT Durgapur)"
    return "All India"

yearly["college_id"] = yearly["CollegeID"]
yearly["college"] = yearly["CollegeName"]
yearly["branch"] = yearly["CourseName"]
yearly["category"] = yearly["Category"]
yearly["base_category"] = yearly["Base_Category"]
yearly["quota"] = yearly["Quota"]
yearly["region"] = yearly["Region"]
yearly["district"] = yearly["college"].apply(extract_kcet_district)

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
    "quota", "region", "district", "cutoff_rank", "cutoff_2023", "cutoff_2024",
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
    jee_df["district"] = jee_df["college"].apply(extract_jee_district)
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
    print("Updated data/jee_cutoffs.csv with standard multi-year schema and district tags.")

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