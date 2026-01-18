from flask import Blueprint, render_template, jsonify
import pickle
import pandas as pd
import os

# Define blueprint
predict_bp = Blueprint(
    "predict",
    __name__,
    template_folder="./templates",  # adjust if templates are in root /templates
    url_prefix="/predict"
)

# Load crop models
MODEL_FILE = os.path.join(os.path.dirname(__file__), "../crop_models.pkl")

with open("crop_models.pkl", "rb") as f:
	models = pickle.load(f)


@predict_bp.route("/")
def home():
    """Render prediction homepage with available crops"""
    crops = list(models.keys())
    return render_template("pre.html", crops=crops)

@predict_bp.route("/<crop>")
def predict_crop(crop):
    """Return prediction for a specific crop"""
    if crop not in models:
        return jsonify({"error": f"No model found for crop: {crop}"}), 404

    model = models[crop]

    # Create future dataframe until Dec 2026
    future = model.make_future_dataframe(periods=72, freq="M")  # 6 years approx.
    forecast = model.predict(future)

    # Filter only 2025–2026 data
    forecast_2025_2026 = forecast[
        (forecast['ds'].dt.year >= 2025) & (forecast['ds'].dt.year <= 2026)
    ][['ds', 'yhat']]

    # Build response
    result = {
        "crop": crop,
        "dates": forecast_2025_2026['ds'].dt.strftime("%Y-%m").tolist(),
        "prices": forecast_2025_2026['yhat'].round(2).tolist()
    }

    return jsonify(result)
    
