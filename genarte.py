
import pandas as pd
import numpy as np
import os

# -----------------------------------------
# STEP 1: Load merged historical weather data
# -----------------------------------------

weather = pd.read_csv("output/combined_weather.csv")

weather["time"] = pd.to_datetime(weather["time"])

weather = weather.sort_values("time").reset_index(drop=True)

# -----------------------------------------
# STEP 2: Extract date-based features
# -----------------------------------------

weather["year"] = weather["time"].dt.year
weather["month"] = weather["time"].dt.month
weather["day"] = weather["time"].dt.day
weather["day_of_week"] = weather["time"].dt.dayofweek
weather["day_of_year"] = weather["time"].dt.dayofyear

# -----------------------------------------
# STEP 3: Generate seasonal variation
# -----------------------------------------

seasonal_effect = 4 * np.sin(
    2 * np.pi * (weather["day_of_year"] - 40) / 365.25
)

# -----------------------------------------
# STEP 4: Generate weekday effect
# -----------------------------------------

weekday_effect = np.where(
    weather["day_of_week"] >= 5,
    -2.0,
    2.0
)

# -----------------------------------------
# STEP 5: Generate controlled random variation
# -----------------------------------------

rng = np.random.default_rng(42)

random_variation = rng.normal(
    loc=0,
    scale=2.5,
    size=len(weather)
)

# -----------------------------------------
# STEP 6: Create simulated electricity demand
# -----------------------------------------

weather["Load_MW"] = (
    95
    + 1.0 * (weather["temp_mean"] - 22)
    + 0.25 * (weather["temp_max"] - 28)
    + seasonal_effect
    + weekday_effect
    + random_variation
)

# Keep demand values positive
weather["Load_MW"] = weather["Load_MW"].clip(lower=10)

weather["Load_MW"] = weather["Load_MW"].round(2)

# -----------------------------------------
# STEP 7: Clearly label simulated data
# -----------------------------------------

weather["Demand_Type"] = "SIMULATED_DEMO"

# -----------------------------------------
# STEP 8: Save the final dataset
# -----------------------------------------

os.makedirs("output", exist_ok=True)

output_file = "output/energy_dataset.csv"

weather.to_csv(output_file, index=False)

# -----------------------------------------
# STEP 9: Display results
# -----------------------------------------

print("\n====================================")
print("SIMULATED ENERGY DATASET CREATED")
print("====================================")

print("Total records:", len(weather))

print("\nDataset columns:")
print(weather.columns.tolist())

print("\nFirst 5 records:")
print(weather.head())

print("\nDemand statistics:")
print(weather["Load_MW"].describe())

print("\nDemand source:")
print(weather["Demand_Type"].unique())

print("\nSaved successfully to:", output_file)
