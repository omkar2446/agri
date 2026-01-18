# network.py
from flask import Blueprint, request, jsonify, send_from_directory
import pandas as pd
import os
from werkzeug.utils import secure_filename
from time import time

network_bp = Blueprint(
    "network",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/network"
)

UPLOAD_FOLDER = os.path.join("static", "uploads")
EXCEL_FILE = "community.xlsx"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(EXCEL_FILE):
    pd.DataFrame(columns=["User", "Content", "Image"]).to_excel(EXCEL_FILE, index=False)

def load_data():
    return pd.read_excel(EXCEL_FILE)

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

@network_bp.route("/")
def home():
    return send_from_directory(network_bp.static_folder, "index.html")

@network_bp.route("/post", methods=["POST"])
def create_post():
    name = request.form.get("name")
    content = request.form.get("content")
    file = request.files.get("image")

    if not name:
        return jsonify({"error": "Name required"}), 400
    if not content and not file:
        return jsonify({"error": "Write something or upload image"}), 400

    filename = ""
    if file:
        filename = f"{int(time())}_{secure_filename(file.filename)}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    df = load_data()
    df.loc[len(df)] = [name, content, filename]
    save_data(df)
    return jsonify({"message": "Post created"}), 201

@network_bp.route("/posts", methods=["GET"])
def get_posts():
    df = load_data()
    posts = []
    for _, row in df.iterrows():
        img_path = ""
        if pd.notna(row["Image"]) and str(row["Image"]).strip() != "":
            img_path = f"/static/uploads/{row['Image']}"
        posts.append({
            "user": row["User"],
            "content": row["Content"] if pd.notna(row["Content"]) else "",
            "image": img_path
        })
    return jsonify(posts)
