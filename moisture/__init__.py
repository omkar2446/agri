from flask import Blueprint, render_template, request, jsonify

moisture_bp = Blueprint(
    "moisture",
    __name__,
    template_folder="templates",
    url_prefix="/moisture"
)

latest_moisture = 0

@moisture_bp.route("/")
def page():
    return render_template("moisture.html")

@moisture_bp.route("/update", methods=["POST"])
def update():
    global latest_moisture
    data = request.json
    latest_moisture = data.get("moisture", 0)
    return jsonify({"status": "received"})

@moisture_bp.route("/data")
def data():
    return jsonify({"moisture": latest_moisture})
