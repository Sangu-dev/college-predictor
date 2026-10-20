# 🎓 KCET & JEE College Predictor

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

An intelligent, data-driven college admission predictor for **KCET (Karnataka CET)** and **JEE Main (National Institutes of Technology)**. Powered by 150,000+ official cutoff trends, instant probability scoring, and an uncluttered dark-mode interface.

---

## 🌟 Highlights & Key Features

### 1. Dual Exam Engine (KCET & JEE Main)
- **KCET (Karnataka CET)**: Covers **460+ engineering institutions**, **146 courses**, and **48 categories/sub-quotas** using official 2023, 2024, and 2025 closing ranks.
- **JEE Main (NITs)**: Covers India's top **10 National Institutes of Technology** (NIT Surathkal, NIT Trichy, NIT Warangal, MNNIT Allahabad, etc.) across 7 years of JoSAA closing ranks (2020–2026).
- **Dynamic Form Adaptation**: The UI automatically swaps categories, branches, and quota options when switching between KCET and JEE.

### 2. Traffic-Light Admission Probability Indicators
Clean, intuitive colored indicators eliminate confusing percentages and bloated tables:
- 🟢 **Green Circle (`Easy to Get`)**: Cutoff rank is comfortably above your rank ($\text{Cutoff} \ge 1.25 \times \text{Rank}$). Safe backup choice with high admission certainty.
- 🟡 **Yellow Circle (`50–50 Chance`)**: Cutoff is close to your rank ($0.85 \times \text{Rank} \le \text{Cutoff} < 1.25 \times \text{Rank}$). Very realistic and competitive choice.
- 🔴 **Red Circle (`Difficult`)**: Cutoff was stricter than your rank ($\text{Cutoff} < 0.85 \times \text{Rank}$). Ambitious reach option during later rounds or special rounds.

### 3. Streamlined 5-Column Clean Results Table
No visual clutter or overwhelming numbers:
1. **Save**: One-click heart icon to bookmark options into your personal counseling shortlist.
2. **College Name & Code**: Official institution code (e.g. `E001`, `NIT08`), full college name, cutoff badge, and Article 371(J) HK quota indicator.
3. **Engineering Branch**: Target engineering branch/specialization.
4. **Category**: Category pill (`GM`, `2AG`, `3BG`, `General`, `OBC-NCL`, etc.).
5. **Admission Chance**: Glowing color circles with clear status text.

### 4. Interactive Counseling Tools
- ⚡ **Instant Live Search**: Filter table results instantly by college name or college code without page reload.
- 🏷️ **Quick Tier Tabs**: Toggle between **All Colleges**, **🟢 Easy to Get**, **🟡 50–50 Chance**, and **🔴 Difficult**.
- 🚀 **1-Click Branch Chips**: Instant presets for CSE, AI & DS, AI & ML, ISE, ECE, EEE, Mechanical, Civil, Cyber Security, and Robotics.
- 💜 **Favourites & Shortlist Dashboard (`/favourites`)**: Review saved colleges, delete choices, or clear all.
- 📄 **Export & Print**: Download your shortlisted options as a clean CSV or print them directly for option-entry preparation.

---

## 📊 Dataset Specifications

| Metric | KCET Dataset | JEE Mains Dataset |
| :--- | :--- | :--- |
| **Total Records** | **151,974 raw records** (47,116 aggregated) | **2,520 records** (360 aggregated) |
| **Years Covered** | 2023, 2024, 2025 | 2020 through 2026 |
| **Colleges** | 460+ Karnataka Engineering Colleges | Top 10 National Institutes of Technology (NITs) |
| **Courses** | 146 Engineering Branches | 6 Core Engineering Specializations |
| **Categories** | 48 Categories (GM, 1G, 2A, 2B, 3A, 3B, SC, ST, Rural, Kannada, HK) | General, OBC-NCL, EWS, SC, ST, PwD |
| **Sources** | Kaggle (`sowmithns/kcet-college-admission...`) | Kaggle (`edudev-commons-org/jee-mains...`) |

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.11, [Flask](https://flask.palletsprojects.com/)
- **Data Processing**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Machine Learning**: [Scikit-learn](https://scikit-learn.org/) (LabelEncoders & Random Forest models)
- **Frontend**: Semantic HTML5, Vanilla CSS, [Bootstrap 5.3](https://getbootstrap.com/), [Bootstrap Icons](https://icons.getbootstrap.com/)
- **Typography**: [Google Fonts (Plus Jakarta Sans)](https://fonts.google.com/specimen/Plus+Jakarta+Sans)
- **Storage**: In-memory caching for sub-millisecond query execution + `localStorage` for offline shortlist persistence

---

## 📁 Project Structure

```text
college_predictor/
│
├── app.py                      # Flask backend, routing, API endpoints & in-memory caching
├── train_model.py              # Data pipeline, multi-year aggregation & model training
├── extract_kcet.py             # PDF extraction script (Camelot)
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── data/
│   ├── kcet_cutoffs.csv        # Curated 47k multi-year KCET cutoff records (2023-2025)
│   ├── kcet_ai_ready.csv       # Raw KCET dataset (151k rows)
│   ├── jee_cutoffs.csv         # Curated 360 multi-year NIT cutoff records (2020-2026)
│   └── jee_mains/              # Raw JEE Mains shift, category & NIT cutoff datasets
│
└── templates/
    ├── index.html              # Modern search portal with dynamic exam switching & chips
    ├── result.html             # Simplified 5-column results table with color circles
    └── favourites.html         # Saved colleges dashboard with CSV export & print support
```

---

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Sangu-dev/college-predictor.git
cd college-predictor
```

### 2. Set Up Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

*(Optional: If downloading datasets directly via code, install `pip install kagglehub`).*

### 4. Run Data Processing & Training (If updating datasets)
```bash
python train_model.py
```

### 5. Launch Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔌 API Endpoints

The Flask application also exposes lightweight JSON endpoints for programmatic access and autocomplete:

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/branches?exam=KCET` | `GET` | Returns list of all available branches for the given exam |
| `/api/categories?exam=KCET`| `GET` | Returns list of valid category codes |
| `/api/colleges?exam=KCET`  | `GET` | Returns list of unique college names and official IDs |
| `/favourites`              | `GET` | Renders user's saved shortlist |

---

## 🎯 How Admission Tiers Work

The predictor uses standard counseling margin formulas to prevent unrealistic predictions:

```text
Let R = Candidate Rank, C = College Closing Cutoff Rank

         Ratio = C / R
┌─────────────────────────────────────────────────────────────┐
│  🟢 Easy to Get     (Ratio ≥ 1.25)                          │
│     Cutoff rank is at least 25% higher than your rank       │
├─────────────────────────────────────────────────────────────┤
│  🟡 50–50 Chance    (0.85 ≤ Ratio < 1.25)                   │
│     Cutoff is within your competitive rank range (±15-25%)  │
├─────────────────────────────────────────────────────────────┤
│  🔴 Difficult       (Ratio < 0.85)                          │
│     Cutoff was more selective; ambitious round 2/3 reach   │
└─────────────────────────────────────────────────────────────┘
```

---

## 👨‍💻 Author

**Sangamesh**  
*Artificial Intelligence & Machine Learning Student*  
GitHub: [@Sangu-dev](https://github.com/Sangu-dev)

---

## 🌟 Support

If this project helped you or provided useful counseling insights, consider giving it a **Star (⭐)** on [GitHub](https://github.com/Sangu-dev/college-predictor)!
