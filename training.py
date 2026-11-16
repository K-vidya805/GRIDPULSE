
import pandas as pd
import numpy as np
import os
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# -----------------------------------------
# STEP 1: Load dataset
# -----------------------------------------

data = pd.read_csv("output/energy_dataset.csv")

data["time"] = pd.to_datetime(data["time"])

data = data.sort_values("time").reset_index(drop=True)

# -----------------------------------------
# STEP 2: Select input features
# -----------------------------------------

features = [
    "RAINFALL (mm)",
    "temp_max",
    "temp_min",
    "temp_mean",
    "month",
    "day",
    "day_of_week",
    "day_of_year"
]

X = data[features]
y = data["Load_MW"]

# -----------------------------------------
# STEP 3: Chronological train-test split
# -----------------------------------------

split_index = int(len(data) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

print(
    "Training period:",
    data["time"].iloc[0].date(),
    "to",
    data["time"].iloc[split_index - 1].date()
)

print(
    "Testing period:",
    data["time"].iloc[split_index].date(),
    "to",
    data["time"].iloc[-1].date()
)

# -----------------------------------------
# STEP 4: Create Random Forest model
# -----------------------------------------

model = RandomForestRegressor(
    n_estimators=150,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)

# -----------------------------------------
# STEP 5: Train model
# -----------------------------------------

print("\nTraining Random Forest model...")

model.fit(X_train, y_train)

print("Model training completed!")

# -----------------------------------------
# STEP 6: Make predictions
# -----------------------------------------

predictions = model.predict(X_test)

# -----------------------------------------
# STEP 7: Evaluate model
# -----------------------------------------

mae = mean_absolute_error(y_test, predictions)

rmse = np.sqrt(mean_squared_error(y_test, predictions))

r2 = r2_score(y_test, predictions)

print("\n===================================")
print("MODEL EVALUATION RESULTS")
print("===================================")

print(f"MAE  : {mae:.3f} MW")
print(f"RMSE : {rmse:.3f} MW")
print(f"R2   : {r2:.4f}")

# -----------------------------------------
# STEP 8: Save test predictions
# -----------------------------------------

results = pd.DataFrame({
    "Date": data["time"].iloc[split_index:].values,
    "Simulated_Load_MW": y_test.values,
    "Predicted_MW": predictions.round(2)
})

os.makedirs("output", exist_ok=True)

results.to_csv(
    "output/model_test_predictions.csv",
    index=False
)

# -----------------------------------------
# STEP 9: Save trained model
# -----------------------------------------

joblib.dump(model, "output/random_forest_model.pkl")

# Save feature names for future use
joblib.dump(features, "output/model_features.pkl")

print("\n===================================")
print("FILES SAVED SUCCESSFULLY")
print("===================================")

print("Model: output/random_forest_model.pkl")
print("Features: output/model_features.pkl")
print("Predictions: output/model_test_predictions.csv")
