from flask import Flask, render_template, request
import pandas as pd
import pickle

app = Flask(__name__)

# Load ML model and encoders
model = pickle.load(open("model.pkl", "rb"))
college_encoder = pickle.load(open("college_encoder.pkl", "rb"))
branch_encoder = pickle.load(open("branch_encoder.pkl", "rb"))
category_encoder = pickle.load(open("category_encoder.pkl", "rb"))


# Load dataset
def load_data(exam):
    if exam == "KCET":
        return pd.read_csv("data/kcet_cutoffs.csv")

    elif exam == "JEE":
        return pd.read_csv("data/jee_cutoffs.csv")


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        # Get form data
        rank = int(request.form["rank"])
        category = request.form["category"]
        branch = request.form["branch"]
        exam = request.form["exam"]

        # Load data
        data = load_data(exam)

        # Convert cutoff rank to numeric
        data["cutoff_rank"] = pd.to_numeric(
            data["cutoff_rank"],
            errors="coerce"
        )

        # Filter colleges
        filtered = data[
            (data["cutoff_rank"] >= rank) &
            (data["category"] == category)
        ]

        # Filter by branch
        if branch != "":
            filtered = filtered[
                filtered["branch"] == branch
            ]

        # ML Prediction
        if branch == "":
            branch_encoded = 0
        else:
            branch_encoded = branch_encoder.transform([branch])[0]
        category_encoded = category_encoder.transform([category])[0]

        prediction = model.predict(
            [[rank, branch_encoded, category_encoded]]
        )

        predicted_college = college_encoder.inverse_transform(
            [int(prediction[0])]
        )[0]
        college_names = filtered["college"].values

        if len(filtered) == 0:
            predicted_college = "No colleges found for this rank/category"

        elif predicted_college not in college_names:
            predicted_college = filtered.iloc[0]["college"]

        print("Predicted College:", predicted_college)

        # Sort colleges
        filtered = filtered.drop_duplicates()
        filtered = filtered.sort_values(
            by="cutoff_rank",
            ascending=True
        )

        # Convert to dictionary
        results = filtered.to_dict(orient="records")

        # AI recommended colleges
        recommended = filtered.head(5)
        recommended = recommended.to_dict(orient="records")

        # Send data to result page
        return render_template(
            "result.html",
            results=results,
            recommended=recommended,
            predicted_college=predicted_college,
            rank=rank,
            category=category,
            exam=exam
        )

    return render_template("index.html")


@app.route("/favourites")
def favourites():
    return render_template("favourites.html")


if __name__ == "__main__":
    app.run(debug=True)