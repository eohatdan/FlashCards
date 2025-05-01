from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Read database config from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT", "5432")

# Optional: Enforce SSL for Supabase
DB_SSL = os.getenv("DB_SSL", "require")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        sslmode=DB_SSL
    )


@app.route("/get_phrases", methods=["GET"])
def get_phrases():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, spanish, english FROM spanish_english ORDER BY id;")
        rows = cur.fetchall()
        phrases = [{"id": row[0], "spanish": row[1], "english": row[2]} for row in rows]
        return jsonify(phrases)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route("/add_phrase", methods=["POST"])
def add_phrase():
    data = request.json
    spanish = data.get("spanish")
    english = data.get("english")
    if not spanish or not english:
        return jsonify({"error": "Missing 'spanish' or 'english'"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO spanish_english (spanish, english) VALUES (%s, %s) RETURNING id;",
            (spanish, english)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"success": True, "id": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route("/edit_phrase", methods=["PUT"])
def edit_phrase():
    data = request.json
    phrase_id = data.get("id")
    spanish = data.get("spanish")
    english = data.get("english")

    if not phrase_id or not spanish or not english:
        return jsonify({"error": "Missing 'id', 'spanish' or 'english'"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE spanish_english SET spanish = %s, english = %s WHERE id = %s;",
            (spanish, english, phrase_id)
        )
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route("/delete_phrase", methods=["DELETE"])
def delete_phrase():
    data = request.json
    phrase_id = data.get("id")

    if not phrase_id:
        return jsonify({"error": "Missing 'id'"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM spanish_english WHERE id = %s;", (phrase_id,))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route("/", methods=["GET"])
def index():
    return "Spanish-English Flashcard API is running."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
