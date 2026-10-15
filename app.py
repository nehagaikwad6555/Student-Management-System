import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect

load_dotenv()

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing in .env")
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )


def create_database():
    db = get_db_connection()
    try:
        with db.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    course TEXT,
                    department TEXT
                )
            """)
        db.commit()
    finally:
        db.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        values = (
            request.form["name"],
            request.form["email"],
            request.form["phone"],
            request.form["course"],
            request.form["department"]
        )

        db = get_db_connection()
        try:
            with db.cursor() as cur:
                cur.execute("""
                    INSERT INTO students
                    (name, email, phone, course, department)
                    VALUES (%s, %s, %s, %s, %s)
                """, values)
            db.commit()
        finally:
            db.close()

        return redirect("/view")

    return render_template("add_student.html")


@app.route("/view")
def view_students():
    db = get_db_connection()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM students ORDER BY id")
            students = cur.fetchall()
    finally:
        db.close()

    return render_template("view_students.html", students=students)


@app.route("/delete/<int:id>")
def delete_student(id):
    db = get_db_connection()
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM students WHERE id = %s", (id,))
        db.commit()
    finally:
        db.close()

    return redirect("/view")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    db = get_db_connection()

    try:
        with db.cursor() as cur:
            if request.method == "POST":
                values = (
                    request.form["name"],
                    request.form["email"],
                    request.form["phone"],
                    request.form["course"],
                    request.form["department"],
                    id
                )

                cur.execute("""
                    UPDATE students
                    SET name = %s, email = %s, phone = %s,
                        course = %s, department = %s
                    WHERE id = %s
                """, values)
                db.commit()
                return redirect("/view")

            cur.execute("SELECT * FROM students WHERE id = %s", (id,))
            student = cur.fetchone()
    finally:
        db.close()

    if student is None:
        return redirect("/view")

    return render_template("edit_student.html", student=student)


@app.route("/search")
def search_student():
    name = request.args.get("name", "")

    db = get_db_connection()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT * FROM students WHERE name ILIKE %s ORDER BY id",
                ("%" + name + "%",)
            )
            students = cur.fetchall()
    finally:
        db.close()

    return render_template("view_students.html", students=students)


create_database()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)