from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
import os

# Load environment variables from .env (in this folder or repo root)
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI not set in environment or .env (see api/README.md)")

# Connect to MongoDB Atlas
client = MongoClient(MONGODB_URI)
db = client["softwarelabdb"]

# Collections (match original names so Load Project works)
users_col = db.get_collection("Users")       # new for auth; will be created on first insert
projects_col = db.get_collection("Projects")
resources_col = db.get_collection("Resources")


# Ensure uniqueness
users_col.create_index("userId", unique=True)
projects_col.create_index("projectId", unique=True)

app = Flask(__name__)

# Allow frontend dev server
CORS(
    app,
    origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    supports_credentials=True,
)

# ---------- AUTH ENDPOINTS ----------

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True) or {}
    user_id = data.get("userId")
    password = data.get("password")

    if not user_id or not password:
        return jsonify({"error": "userId and password are required"}), 400

    doc = {
        "userId": user_id,
        "password": password,  # for class/demo only; don't do this in real life :)
    }

    try:
        users_col.insert_one(doc)
    except DuplicateKeyError:
        return jsonify({"error": "User already exists"}), 409

    return jsonify({"ok": True, "userId": user_id}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    user_id = data.get("userId")
    password = data.get("password")

    if not user_id or not password:
        return jsonify({"error": "userId and password are required"}), 400

    user = users_col.find_one({"userId": user_id})
    if not user or user.get("password") != password:
        # Covers: wrong password OR non-existent user
        return jsonify({"error": "Invalid userId/password"}), 401

    # Simple response so frontend can store/log state
    return jsonify({"ok": True, "userId": user_id}), 200


# ---------- PROJECT ENDPOINTS (already in your README spec) ----------

@app.route("/api/projects", methods=["GET"])
def list_projects():
    docs = list(
        projects_col.find(
            {},
            {"_id": 0, "projectId": 1, "name": 1, "description": 1, "createdAt": 1},
        )
    )
    return jsonify(docs), 200


@app.route("/api/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    doc = projects_col.find_one(
        {"projectId": project_id},
        {"_id": 0, "projectId": 1, "name": 1, "description": 1, "createdAt": 1},
    )
    if not doc:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(doc), 200


@app.route("/api/projects", methods=["POST"])
def create_project():
    payload = request.get_json(force=True) or {}
    required = ("projectId", "name")
    if not all(k in payload and payload[k] for k in required):
        return jsonify({"error": "projectId and name are required"}), 400

    doc = {
        "projectId": payload["projectId"],
        "name": payload["name"],
        "description": payload.get("description", ""),
        "createdAt": payload.get("createdAt"),
    }

    try:
        projects_col.insert_one(doc)
    except DuplicateKeyError:
        return jsonify({"error": "projectId already exists"}), 409

    return jsonify({"ok": True, "projectId": doc["projectId"]}), 201


# (Optional stub for resources if needed later)
@app.route("/api/projects/<project_id>/resources", methods=["GET"])
def get_project_resources(project_id):
    docs = list(
        resources_col.find(
            {"projectId": project_id},
            {"_id": 0, "projectId": 1, "setId": 1, "total": 1,
             "allocatedToProject": 1, "available": 1, "notes": 1},
        )
    )
    return jsonify(docs), 200


if __name__ == "__main__":
    # Runs on http://127.0.0.1:5000
    app.run(host="127.0.0.1", port=5000, debug=True)
