import os
import numpy as np
import cv2
from flask import Blueprint, render_template, request, jsonify
from keras.models import load_model
from datetime import datetime

# =========================
# Create Blueprint
# =========================
project_bp = Blueprint(
    "project",
    __name__,
    template_folder="templates",
    url_prefix="/project"
)

# =========================
# Load Model
# =========================
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.h5")

try:
    model = load_model(MODEL_PATH, compile=False)
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Failed to load model:", e)
    model = None

# =========================
# Labels (AS YOU WANT)
# =========================
labels = {
    0: "Healthy",
    1: "Powdery",
    2: "Rust"
}

# =========================
# Greeting Helper
# =========================
def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning! 🌞"
    elif 12 <= hour < 17:
        return "Good Afternoon! 🌾"
    elif 17 <= hour < 22:
        return "Good Evening! 🌙"
    else:
        return "Hello, working late? 🌱"

# =========================
# 🔥 Prediction Function
# =========================
def getResult(image_bytes):
    """
    Takes image bytes and returns (label, confidence)
    """

    # Decode image
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Invalid image")

    # Preprocess (MUST match training size)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    # Predict
    preds = model.predict(img)[0]
    class_index = int(np.argmax(preds))
    confidence = float(np.max(preds))

    return labels[class_index], confidence

# =========================
# Routes
# =========================
@project_bp.route("/")
def home():
    return render_template("project.html", greeting=get_greeting())

@project_bp.route("/predict", methods=["POST"])
def predict():
    try:
        print("FILES RECEIVED:", request.files)

        if model is None:
            return jsonify({"error": "Model not loaded"}), 500

        # ✅ Accept both "image" and "file"
        if "image" in request.files:
            image_file = request.files["image"]
        elif "file" in request.files:
            image_file = request.files["file"]
        else:
            return jsonify({"error": "No image uploaded"}), 400

        image_bytes = image_file.read()

        prediction, confidence = getResult(image_bytes)

        return jsonify({
            "prediction": prediction,
            "confidence": round(confidence, 3)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
