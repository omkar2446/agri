import os
import numpy as np
import cv2
from flask import Blueprint, render_template, request, jsonify
from keras.models import load_model

# Create Blueprint
project_bp = Blueprint(
    "project",
    __name__,
    template_folder="templates",
    url_prefix="/project"   # 🔥 THIS LINE FIXES EVERYTHING
)
 

# Path to model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "plant_disease_model.h5")

# Load model
try:
    model = load_model(MODEL_PATH, compile=False)
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Failed to load model:", e)
    model = None

# Class labels
CLASS_NAMES = ('Tomato-Bacterial_spot', 'Potato-Early_blight', 'Corn-Common_rust')

# Helper: Greeting
from datetime import datetime
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

# Routes
@project_bp.route("/")
def home():
    return render_template("project.html", greeting=get_greeting())

@project_bp.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"].read()
    npimg = np.frombuffer(file, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Preprocess
    img = cv2.resize(img, (256, 256))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    # Predict
    preds = model.predict(img)
    result = CLASS_NAMES[np.argmax(preds)]
    confidence = float(np.max(preds))

    return jsonify({
        "prediction": result,
        "confidence": round(confidence, 3)
    })
