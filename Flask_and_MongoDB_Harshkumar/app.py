"""Flask & MongoDB assignment.

Routes
------
GET  /api      -> returns a JSON list read from the backend file data.json
GET  /         -> frontend form (it posts back to the same URL)
POST /         -> inserts the form data into MongoDB Atlas
                  success -> redirect to /success ("Data submitted successfully")
                  error   -> same page is shown again with the error (no redirect)
GET  /success  -> success page
"""
import json
import os
import re
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from pymongo import MongoClient

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "flask_assignment")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "submissions")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = Flask(__name__)

_client = None


def get_collection():
    """Return the MongoDB Atlas collection (client is created once)."""
    global _client
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is not set. Add your Atlas connection string to the .env file.")
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client[DB_NAME][COLLECTION_NAME]


# ---------------------------------------------------------------- Task 1
@app.route("/api")
def api():
    """Read the list from the backend file and send it as a JSON response."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        return jsonify({"error": f"Could not read data file: {exc}"}), 500
    return jsonify(data)


# ---------------------------------------------------------------- Task 2
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("form.html", error=None, form={})

    form = {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "message": request.form.get("message", "").strip(),
    }

    # Validation: on error show the message on the same page, no redirect.
    if not form["name"] or not form["email"] or not form["message"]:
        return render_template("form.html", error="All fields are required.", form=form), 400
    if not EMAIL_RE.match(form["email"]):
        return render_template("form.html", error="Please enter a valid email address.", form=form), 400

    try:
        get_collection().insert_one({**form, "created_at": datetime.now(timezone.utc)})
    except Exception as exc:  # connection failure, auth failure, bad URI, ...
        return render_template("form.html", error=f"Database error: {exc}", form=form), 500

    # Success: redirect to another page.
    return redirect(url_for("success"))


@app.route("/success")
def success():
    return render_template("success.html", message="Data submitted successfully")


if __name__ == "__main__":
    app.run(debug=True)
