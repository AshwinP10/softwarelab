from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
import os


load_dotenv()  # will read .env from repo root if present

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI not set in environment or .env (see api/README.md)")

client = MongoClient(MONGODB_URI)
db = client.get_database("softwarelabdb")
projects_col = db.get_collection("Projects")

# safe to call at startup
projects_col.create_index("projectId", unique=True)

# ensure resources collection index for fast lookup by projectId
resources_col = db.get_collection("Resources")
resources_col.create_index({"projectId": 1})

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})


@app.route("/api/projects", methods=["GET"])
def list_projects():
    docs = list(projects_col.find({}, {"_id": 0, "projectId": 1, "name":1, "description":1, "createdAt":1}))
    return jsonify(docs), 200


@app.route("/api/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    doc = projects_col.find_one({"projectId": project_id})
    if not doc:
        return jsonify({"error": "not found"}), 404
    # map _id to id string and remove raw _id
    doc["id"] = str(doc.get("_id"))
    doc.pop("_id", None)
    return jsonify(doc), 200


@app.route("/api/projects/<project_id>/resources", methods=["GET"])
def get_project_resources(project_id):
    try:
        docs = list(resources_col.find({"projectId": project_id}, {"_id": 0, "hwsetId":1, "name":1, "total":1, "allocatedToProject":1, "available":1, "notes":1}))
        return jsonify(docs), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to fetch resources"}), 500


@app.route("/api/projects", methods=["POST"])
def create_project():
    payload = request.get_json(force=True)
    required = ["projectId", "name"]
    for r in required:
        if r not in payload or not payload[r]:
            return jsonify({"error": f"missing field {r}"}), 400

    doc = {
        "projectId": payload["projectId"],
        "name": payload["name"],
        "description": payload.get("description", ""),
        "createdAt": payload.get("createdAt")
    }

    try:
        projects_col.insert_one(doc)
    except DuplicateKeyError:
        return jsonify({"error": "projectId already exists"}), 409
    return jsonify({"ok": True, "projectId": doc["projectId"]}), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
