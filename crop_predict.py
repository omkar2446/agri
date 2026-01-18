import pandas as pd
import pickle
from prophet import Prophet   # pip install prophet

# --- 1. Load and Prepare the Data ---
try:
    df = pd.read_excel(
        'maharashtra_crop_price_SAMPLE_EXPANDED_2000-2020.xlsx',
        sheet_name="Sheet1"
    )
    print("✅ Successfully loaded the dataset.")
except FileNotFoundError:
    print("❌ Error: Make sure the Excel file is in the same folder as this script.")
    exit()

# Convert 'Date' to datetime
df['Date'] = pd.to_datetime(df['Date'])

# --- 2. Train Models for Each Crop ---
models = {}
crops = df['Commodity'].unique()

for crop in crops:
    crop_df = df[df['Commodity'] == crop][['Date', 'Modal_Price']].copy()

    # Prophet needs columns "ds" (date) and "y" (value)
    crop_df.rename(columns={'Date': 'ds', 'Modal_Price': 'y'}, inplace=True)

    # Resample monthly for smoother forecasting
    crop_df = crop_df.resample('M', on='ds').mean().reset_index()

    # Fill missing values
    crop_df['y'] = crop_df['y'].fillna(method="bfill")

    # Train Prophet model
    model = Prophet(yearly_seasonality=True, daily_seasonality=False)
    model.fit(crop_df)

    # Save model
    models[crop] = model
    print(f"🌾 Trained model for {crop}")

# --- 3. Save All Models ---
model_filename = 'crop_models.pkl'
with open(model_filename, 'wb') as f:
    pickle.dump(models, f)

print(f"\n💾 All crop models saved in {model_filename}")
print("✅ You can now run the Flask app to predict for 2025–2026!")
