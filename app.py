
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os

# -----------------------------------------
# STEP 1: Initialize Flask application
# -----------------------------------------

app = Flask(__name__)
CORS(app)

# -----------------------------------------
# STEP 2: Load trained model and features
# -----------------------------------------

MODEL_PATH = "output/random_forest_model.pkl"
FEATURE_PATH = "output/model_features.pkl"

model = joblib.load(MODEL_PATH)
features = joblib.load(FEATURE_PATH)

# -----------------------------------------
# STEP 3: Home route
# -----------------------------------------

@app.route("/")
def home():
    return """
    <h1>GRIDPULSE - Energy Forecasting</h1>
    <p>Belagavi North Demonstration System</p>
    <p>Flask backend is running successfully!</p>
    <p>Demand values are simulated for demonstration.</p>
    """

# -----------------------------------------
# STEP 4: Health check route
# -----------------------------------------

@app.route("/api/status")
def status():
    return jsonify({
        "status": "success",
        "message": "GRIDPULSE backend is running",
        "model": "Random Forest",
        "data_type": "SIMULATED DEMO"
    })

# -----------------------------------------
# STEP 5: Prediction route
# -----------------------------------------

@app.route("/api/predict", methods=["POST"])
def predict():

    try:
        input_data = request.get_json()

        # Check whether all features are provided
        missing_features = [
            feature for feature in features
            if feature not in input_data
        ]

        if missing_features:
            return jsonify({
                "error": "Missing input features",
                "missing_features": missing_features
            }), 400

        # Prepare input for prediction
        input_df = pd.DataFrame(
            [[input_data[feature] for feature in features]],
            columns=features
        )

        # Generate prediction
        prediction = model.predict(input_df)[0]

        return jsonify({
            "status": "success",
            "predicted_demand_MW": round(float(prediction), 2),
            "data_type": "SIMULATED DEMO"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400

    # -----------------------------------------
# STEP 6: Historical data route
# -----------------------------------------

@app.route("/api/history")
def history():

    try:
        data = pd.read_csv("output/energy_dataset.csv")
        data["time"] = pd.to_datetime(data["time"])
        data = data.sort_values("time").tail(30)

        records = []

        for _, row in data.iterrows():
            records.append({
                "date": row["time"].strftime("%Y-%m-%d"),
                "demand": float(row["Load_MW"]),
                "temperature": float(row["temp_mean"]),
                "rainfall": float(row["RAINFALL (mm)"])
            })

        return jsonify({
            "status": "success",
            "data_type": "SIMULATED DEMO",
            "records": records
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------
# STEP 6: Run Flask server
# -----------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )

# -----------------------------------------
# STEP 7: Historical data API
# -----------------------------------------

@app.route("/api/history")
def history():

    try:
        data = pd.read_csv("output/energy_dataset.csv")

        data["time"] = pd.to_datetime(data["time"])

        data = data.sort_values("time").tail(30)

        records = []

        for _, row in data.iterrows():
            records.append({
                "date": row["time"].strftime("%Y-%m-%d"),
                "demand": float(row["Load_MW"]),
                "temperature": float(row["temp_mean"]),
                "rainfall": float(row["RAINFALL (mm)"])
            })

        return jsonify({
            "status": "success",
            "data_type": "SIMULATED DEMO",
            "records": records
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
