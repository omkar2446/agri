from flask import Blueprint, request, jsonify, render_template
import google.generativeai as genai
from datetime import datetime

# Create Blueprint
ai_bp = Blueprint("ai", __name__, template_folder="templates", url_prefix="/ai")

# Configure Gemini
API_KEY = "AIzaSyASjeKSWrcGm4jOoDnsE0cFiMRFXCQ-Ak8"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Greeting helper
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

# Routes inside the Blueprint
@ai_bp.route("/")
def ai_home():
    return render_template("ai.html", greeting=get_greeting())

@ai_bp.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message", "")

    try:
        prompt = f"""
        You are a professional Farming Assistant 🌱. 
        Provide detailed answers about soil, crops, irrigation, fertilizers, and pest management.
        Even if the user only types one word, reply with a full explanation.

        User question: {user_input}
        """

        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})
