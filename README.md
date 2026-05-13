# 🎓 KCET College Predictor

An AI-powered KCET college predictor built using Flask and Machine Learning.

## 🚀 Features
- Predict colleges based on:
  - KCET Rank
  - Category
  - Branch
- ML-based prediction
- Mobile responsive UI
- Favourite colleges feature
- Search functionality

## 🛠 Technologies Used
- Python
- Flask
- Pandas
- Scikit-learn
- HTML
- CSS
- Bootstrap

## ▶️ Run Locally

Clone the repository:

```bash
git clone https://github.com/Sangu-dev/college-predictor.git  

## 📁 Project Structure

college-predictor/
│
├── app.py
├── train_model.py
├── extract_kcet.py
├── requirements.txt
├── README.md
│
├── data/
│   └── kcet_cutoffs.csv
│
├── templates/
│   ├── index.html
│   ├── result.html
│   └── favourites.html
│
└── .gitignore

## 🎯 Project Objective

The main goal of this project is to help KCET students predict possible engineering colleges based on:

- KCET Rank
- Category
- Branch Preference

The system uses Machine Learning to provide intelligent college predictions using previous KCET cutoff data.

---

## ⚙️ How It Works

1. User enters:
   - KCET Rank
   - Category
   - Branch

2. Flask backend receives the input.

3. Input values are encoded using LabelEncoder.

4. Machine Learning model predicts suitable colleges.

5. Matching colleges are filtered from the dataset.

6. Results are displayed in a responsive web interface.

---

## 🧠 Machine Learning Used

This project uses:

- Scikit-learn
- Label Encoding
- Classification Model
- Dataset Filtering
- Data Preprocessing

The ML model is trained using historical KCET cutoff data.

---

## 📊 Dataset Information

Dataset contains:

- College Names
- Branches
- Categories
- Cutoff Ranks

Source:
- KCET cutoff data

---

## 💡 Key Features

✔ KCET College Prediction  
✔ Mobile Responsive UI  
✔ Search Functionality  
✔ Favourite Colleges Feature  
✔ Dynamic Filtering  
✔ Clean Dark UI  
✔ Machine Learning Integration  

---

## 📱 Responsive Design

The frontend is fully responsive and works on:

- Mobile Phones
- Tablets
- Laptops
- Desktop Screens

Bootstrap is used for responsive layouts.

---

## 🚀 Future Enhancements

Planned future improvements:

- AI Chatbot for Counselling
- College Comparison
- Charts & Analytics
- User Login System
- Database Integration
- Real-time Prediction Accuracy Improvement
- Deployment on Cloud

---

## 👨‍💻 Author

Developed by Sangamesh  
Artificial Intelligence & Machine Learning Student

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub.
