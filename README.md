# KCET & JEE College Predictor

KCET & JEE College Predictor is a web application that helps students discover eligible engineering colleges based on their entrance exam ranks. It analyzes historical cutoff closing ranks for KCET (Karnataka CET) and JEE Main (NITs) to predict admission possibilities across different branches and categories. The tool also provides helpful counseling details, including fee structures, campus locations, and round-wise cutoffs.

---

## Key Features

- **Dual Exam Support**: Predicts admissions for KCET (460+ Karnataka engineering colleges) and JEE Main (Top 10 NITs).
- **Admission Probability Tiers**: Groups colleges into **Safe**, **Target**, and **Dream** categories based on candidate rank.
- **District & Region Filters**: Easily filter colleges by Karnataka regional zones or NIT campus states.
- **Multi-Year Cutoff Trends**: View historical closing ranks from past counseling years to track cutoff changes.
- **College Insights & Fees**: View estimated government/private fee ranges, SNQ quota fee waivers, and university affiliations.
- **Round-by-Round Breakdown**: See expected cutoff progression across Round 1, Round 2, and Extended/Special rounds.
- **Shortlist & CSV Export**: Bookmark favorite options and export a personalized shortlist to CSV for counseling option entry.

---

## Tech Stack

- **Backend**: Python 3.10+, Flask
- **Data & Machine Learning**: Pandas, NumPy, Scikit-learn
- **Frontend**: HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons
- **Data Extraction**: Camelot (PDF table parsing)
- **Storage**: In-memory caching and browser `localStorage`

---

## Project Structure

```text
college_predictor/
├── app.py              # Flask server, prediction routes, and API endpoints
├── train_model.py      # Data preprocessing, trend calculation, and ML training
├── extract_kcet.py     # PDF cutoff table extraction utility
├── requirements.txt    # Project dependencies
├── README.md           # Project documentation
├── data/               # Cutoff datasets for KCET and JEE Main
└── templates/          # Web page templates (index, result, favourites)
```

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Sangu-dev/college-predictor.git
   cd college-predictor
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open in your browser:**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

*(Optional: Run `python train_model.py` if you wish to re-aggregate datasets and retrain the machine learning encoders.)*

---

## Usage

1. **Select Exam**: Choose between **KCET** or **JEE Main**.
2. **Enter Details**: Input your exam rank, reservation category, preferred engineering branch, and district.
3. **View Predictions**: Click **Predict Colleges** to see matching colleges sorted by admission chance.
4. **Inspect Details**: Click any college row to view detailed fee breakdowns, affiliation status, and round-by-round cutoffs.
5. **Save Shortlist**: Click the bookmark icon to save colleges to your **Favourites** list (`/favourites`) and download them as a CSV.

---

## Future Improvements

- Add cutoff datasets for COMEDK UGET and JEE Advanced (IITs).
- Automate cutoff data updates directly from official counseling portals.
- Add an automated option-entry order generator based on student priorities.
- Enable user accounts for cloud-synced counseling shortlists across devices.

---

## Author

**Sangamesh**  
GitHub: [@Sangu-dev](https://github.com/Sangu-dev)

---

## License

This project is licensed under the MIT License.
