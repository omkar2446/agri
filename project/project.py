import os
import numpy as np
import cv2
from flask import Flask, render_template, request, jsonify
from keras.models import load_model
from datetime import datetime

# =========================
# Create Flask App
# =========================
app = Flask(__name__, template_folder="templates")

# =========================
# Load Model
# =========================
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.h5")

try:
    model = load_model(MODEL_PATH, compile=False)
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Model load failed:", e)
    model = None

# =========================
# Class Names (MATCH TRAINING ORDER)
# =========================
CLASS_NAMES = [
    "Tomato-Bacterial_spot",
    "Tomato-Early_blight",
    "Tomato-Late_blight",
    "Potato-Early_blight",
    "Potato-Late_blight",
    "Corn-Common_rust",
    "Corn-Gray_leaf_spot",
    "Corn-Healthy"
]

# =========================
# Greeting Function
# =========================
def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning 🌞"
    elif 12 <= hour < 17:
        return "Good Afternoon 🌾"
    elif 17 <= hour < 22:
        return "Good Evening 🌙"
    else:
        return "Hello 🌱"

# =========================
# Routes
# =========================
@app.route("/")
def home():
    return render_template("project.html", greeting=get_greeting())

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if model is None:
            return jsonify({"error": "Model not loaded"}), 500

        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"].read()
        npimg = np.frombuffer(file, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        # ===== Preprocess (MUST match training) =====
        img = cv2.resize(img, (256, 256))
        img = img / 255.0
        img = np.expand_dims(img, axis=0)

        # ===== Prediction =====
        preds = model.predict(img)[0]
        class_index = int(np.argmax(preds))
        confidence = float(np.max(preds))

        return jsonify({
            "prediction": CLASS_NAMES[class_index],
            "confidence": round(confidence, 3)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# Run App
# =========================
if __name__ == "__main__":
    app.run(debug=True)
