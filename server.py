from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
print("Flashcards server started!")  # or "Seniors Meds server started!"

app = Flask(__name__)
CORS(app)  # Allow all origins (or specify CORS(app, origins=["https://your-frontend"]))

# Get environment variables from Render dashboard
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_PORT = os.environ.get("DB_PORT", 5432)

# Connect to Supabase/Postgres
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

@app.route("/get_phrases", methods=["GET"])
def get_phrases():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT Spanish, English FROM spanish_english;")
        rows = cur.fetchall()
        phrases = [{"spanish": row[0], "english": row[1]} for row in rows]
        cur.close()
        conn.close()
        return jsonify(phrases)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/add_phrase", methods=["POST"])
def add_phrase():
    data = request.get_json()
    spanish = data.get("spanish")
    english = data.get("english")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO spanish_english (Spanish, English) VALUES (%s, %s);", (spanish, english))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/edit_phrase", methods=["POST"])
def edit_phrase():
    data = request.get_json()
    old_spanish = data.get("old_spanish")
    new_spanish = data.get("new_spanish")
    new_english = data.get("new_english")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE spanish_english SET Spanish = %s, English = %s WHERE Spanish = %s;",
            (new_spanish, new_english, old_spanish)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete_phrase", methods=["POST"])
def delete_phrase():
    data = request.get_json()
    spanish = data.get("spanish")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM spanish_english WHERE Spanish = %s;", (spanish,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required to run locally and on Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

