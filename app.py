from flask import Flask, render_template, request, jsonify

app = Flask(__name__)




@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add")
def add_page():
    return render_template("add.html")

@app.route("/search")
def search_page():
    return render_template("search.html")

import sqlite3

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            deadline TEXT,
            priority TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/assignments", methods=["GET", "POST"])
def assignments_api():
    conn = get_db_connection()

    if request.method == "POST":
        data = request.json

        if not data.get("course") or not data.get("title"):
            return jsonify({"error": "Course and title are required"}), 400

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO assignments (course, title, description, deadline, priority, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["course"],
            data["title"],
            data.get("description", ""),
            data.get("deadline", ""),
            data.get("priority", "Low"),
            "pending"
        ))

        assignment_id = cursor.lastrowid
        conn.commit()

        created_assignment = conn.execute(
            "SELECT * FROM assignments WHERE id = ?",
            (assignment_id,)
        ).fetchone()

        conn.close()

        return jsonify(dict(created_assignment)), 201


    # -------- GET --------
    course = request.args.get("course")
    status = request.args.get("status")

    query = "SELECT * FROM assignments WHERE 1=1"
    params = []

    if course:
        query += " AND LOWER(course) = LOWER(?)"
        params.append(course)

    if status:
        query += " AND status = ?"
        params.append(status)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows]), 200

@app.route("/assignments/<int:id>", methods=["PUT", "DELETE"])
def assignment_detail(id):
    conn = get_db_connection()
    assignment = conn.execute(
        "SELECT * FROM assignments WHERE id = ?", (id,)
    ).fetchone()

    if not assignment:
        conn.close()
        return jsonify({"error": "Assignment not found"}), 404

    if request.method == "PUT":
        data = request.json

        conn.execute("""
            UPDATE assignments
            SET course = ?, title = ?, description = ?, deadline = ?, priority = ?, status = ?
            WHERE id = ?
        """, (
            data.get("course", assignment["course"]),
            data.get("title", assignment["title"]),
            data.get("description", assignment["description"]),
            data.get("deadline", assignment["deadline"]),
            data.get("priority", assignment["priority"]),
            data.get("status", assignment["status"]),
            id
        ))

        conn.commit()
        conn.close()
        return jsonify({"message": "Assignment updated"}), 200


    # DELETE
    conn.execute("DELETE FROM assignments WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Assignment deleted"}), 200


@app.route("/edit/<int:id>")
def edit_page(id):
    conn = get_db_connection()
    assignment = conn.execute(
        "SELECT * FROM assignments WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    if not assignment:
        return "Assignment not found", 404

    return render_template("edit.html", assignment=assignment)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
