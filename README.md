# KCET & JEE College Predictor

An admission prediction and counseling analytics platform for Karnataka Common Entrance Test (KCET) and JEE Main (NITs). Built with Flask, Pandas, and Scikit-learn, the application evaluates multi-year cutoff trends to provide candidates with data-driven probability tiers, regulatory fee classifications, and round-by-round seat allotment insights.

---

## Key Features

- **Dual Examination Coverage**: Evaluates closing ranks for **KCET** (460+ engineering institutions, 146 branches, 48 category quotas) and **JEE Main** (Top 10 National Institutes of Technology across 10 campus states).
- **Probability Tier Classification**: Categorizes admission feasibility into **Safe** ($\ge 1.25\times$), **Target** ($0.85\times - 1.24\times$), and **Dream** ($< 0.85\times$) based on candidate rank against closing cutoffs.
- **Geographic Zone Filtering**: Categorizes institutions into 6 Karnataka regional zones (Bengaluru Urban & Rural, Central & Southern, Hubballi-Dharwad & Belagavi, Mysuru & Mandya, Kalyana Karnataka, and Coastal) and All India NIT campus states.
- **Multi-Year Trend Analysis**: Aggregates historical cutoff records (2023–2025 for KCET, 2020–2026 for JEE) with canonical institution mapping to track year-over-year rank shifts.
- **Institutional & Fee Insights**: Displays regulatory fee ranges (KEA-KUPECA government, aided, autonomous, deemed, and JoSAA central rates), Supernumerary Quota (SNQ) waivers, and affiliation details.
- **Round-by-Round Progression**: Simulates seat allotment likelihood across Round 1, Round 2, and Extended / CSAB Special Rounds.
- **Counseling Shortlist & Export**: Local persistence for bookmarking preferred institutions with export to CSV and printable option-entry formats.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.10+, Flask 3 |
| **Data & ML** | Pandas, NumPy, Scikit-learn (RandomForestRegressor, LabelEncoder) |
| **Frontend** | HTML5, Vanilla CSS, Bootstrap 5.3, Bootstrap Icons |
| **Data Extraction** | Camelot (PDF table parsing) |
| **Data Storage** | In-memory dataset caching, browser `localStorage` |

---

## Project Structure

```text
college_predictor/
├── app.py                  # Flask application routes, caching, and prediction engine
├── train_model.py          # Data cleaning, regional tagging, trend calculation & ML training
├── extract_kcet.py         # KEA PDF cutoff table extraction utility
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
├── data/
│   ├── kcet_cutoffs.csv    # Processed KCET dataset with district tags (2023–2025)
│   ├── kcet_ai_ready.csv   # Raw KCET multi-year cutoff records
│   ├── jee_cutoffs.csv     # Curated NIT cutoff records (2020–2026)
│   └── jee_mains/          # Raw JEE category and shift analysis datasets
└── templates/
    ├── index.html          # Search portal and exam parameter selection
    ├── result.html         # Prediction results, interactive filters & detail modal
    └── favourites.html     # Shortlisted colleges dashboard with CSV export
```

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Sangu-dev/college-predictor.git
cd college-predictor
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## How to Run

### 1. Data Pipeline & Model Training (Optional)
To regenerate multi-year aggregations, district tags, and model encoders from raw data:
```bash
python train_model.py
```

### 2. Start the Application
```bash
python app.py
```

Access the application in your browser at:
```
http://127.0.0.1:5000
```

---

## Admission Probability Logic

Admission probability is determined using the ratio of the historical closing cutoff rank ($C$) to the candidate's rank ($R$):

$$\text{Ratio} = \frac{C}{R}$$

| Tier | Ratio Threshold | Definition & Counseling Strategy |
| :--- | :---: | :--- |
| **Safe (Easy)** | $\text{Ratio} \ge 1.25$ | Cutoff rank is at least 25% higher than candidate rank. High admission certainty for backup choices. |
| **Target (50–50)** | $0.85 \le \text{Ratio} < 1.25$ | Cutoff is within competitive range ($\pm 15\text{--}25\%$). Realistic choices for primary allotment rounds. |
| **Dream (Difficult)** | $\text{Ratio} < 0.85$ | Cutoff is stricter than candidate rank. Ambitious reach choices for second extended or special vacancy rounds. |

---

## API Documentation

The application provides lightweight REST endpoints for dynamic querying:

| Endpoint | Method | Query Parameters | Description |
| :--- | :---: | :--- | :--- |
| `/api/districts` | `GET` | `exam` (`KCET` \| `JEE`) | Returns list of geographic zones/districts. |
| `/api/branches` | `GET` | `exam` (`KCET` \| `JEE`) | Returns available branches for the selected exam. |
| `/api/categories` | `GET` | `exam` (`KCET` \| `JEE`) | Returns supported reservation categories. |
| `/api/colleges` | `GET` | `exam` (`KCET` \| `JEE`) | Returns unique institutions with IDs and names. |
| `/api/college_details` | `GET` | `college`, `exam`, `college_id`, `cutoff`, `rank` | Returns institution metadata, fee structures, and round breakdown. |
| `/favourites` | `GET` | — | Renders the candidate's saved shortlist view. |

---

## Future Improvements

- Integration of COMEDK UGET and JEE Advanced (IIT) cutoff datasets.
- Automated ingestion pipeline for official KEA counseling seat allotment notifications.
- Algorithmic option-entry preference list generator optimized for cutoff variance.
- User authentication and cloud persistence for cross-device shortlist synchronization.

---

## Author

**Sangamesh**  
GitHub: [@Sangu-dev](https://github.com/Sangu-dev)

---

## License

This project is licensed under the MIT License.
