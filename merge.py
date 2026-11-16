
import pandas as pd
import os

# STEP 1: Create output folder
os.makedirs("output", exist_ok=True)


# STEP 2: Read CSV files
rainfall = pd.read_csv("Belagavi_North.csv")
temperature = pd.read_csv("temperature.csv")


# STEP 3: Clean column names
rainfall.columns = rainfall.columns.str.strip()
temperature.columns = temperature.columns.str.strip()

print("Rainfall columns:", rainfall.columns.tolist())
print("Temperature columns:", temperature.columns.tolist())


# STEP 4: Function to handle different date formats
def convert_dates(date_column):

    dates = date_column.astype(str).str.strip()

    # First try YYYY-MM-DD
    converted = pd.to_datetime(
        dates,
        format="%Y-%m-%d",
        errors="coerce"
    )

    # For dates not converted, try DD-MM-YYYY
    missing = converted.isna()

    converted.loc[missing] = pd.to_datetime(
        dates.loc[missing],
        format="%d-%m-%Y",
        errors="coerce"
    )

    # Check for invalid dates
    if converted.isna().any():
        invalid_dates = dates[converted.isna()].unique()
        raise ValueError(
            f"Invalid date values found: {invalid_dates[:10]}"
        )

    return converted


# STEP 5: Convert date columns
rainfall["time"] = convert_dates(rainfall["time"])
temperature["time"] = convert_dates(temperature["time"])


# STEP 6: Merge datasets using common dates
combined = pd.merge(
    rainfall,
    temperature,
    on="time",
    how="inner"
)


# STEP 7: Sort by date
combined = combined.sort_values("time")


# STEP 8: Save merged dataset
combined.to_csv(
    "output/combined_weather.csv",
    index=False
)


# STEP 9: Display results
print("\n================================")
print("WEATHER DATA MERGING COMPLETED")
print("================================")

print("Rainfall records:", len(rainfall))
print("Temperature records:", len(temperature))
print("Merged records:", len(combined))

print("\nMerged columns:")
print(combined.columns.tolist())

print("\nFirst 5 records:")
print(combined.head())

print("\nLast 5 records:")
print(combined.tail())

print("\nMissing values:")
print(combined.isnull().sum())

print("\nFile saved at: output/combined_weather.csv")
