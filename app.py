from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "student_management.db"


def get_db_connection():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def create_database():
    db = get_db_connection()

    db.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            course TEXT,
            department TEXT
        )
    """)

    db.commit()
    db.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]
        department = request.form["department"]

        db = get_db_connection()

        db.execute("""
            INSERT INTO students
            (name, email, phone, course, department)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, phone, course, department))

        db.commit()
        db.close()

        return redirect("/")

    return render_template("add_student.html")


@app.route("/view")
def view_students():
    db = get_db_connection()

    students = db.execute(
        "SELECT * FROM students"
    ).fetchall()

    db.close()

    return render_template(
        "view_students.html",
        students=students
    )


@app.route("/delete/<int:id>")
def delete_student(id):
    db = get_db_connection()

    db.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    db.commit()
    db.close()

    return redirect("/view")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    db = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]
        department = request.form["department"]

        db.execute("""
            UPDATE students
            SET name = ?,
                email = ?,
                phone = ?,
                course = ?,
                department = ?
            WHERE id = ?
        """, (name, email, phone, course, department, id))

        db.commit()
        db.close()

        return redirect("/view")

    student = db.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    db.close()

    return render_template(
        "edit_student.html",
        student=student
    )


@app.route("/search")
def search_student():
    name = request.args.get("name", "")

    db = get_db_connection()

    students = db.execute(
        "SELECT * FROM students WHERE name LIKE ?",
        ("%" + name + "%",)
    ).fetchall()

    db.close()

    return render_template(
        "view_students.html",
        students=students
    )


if __name__ == "__main__":
    create_database()
    app.run(host="0.0.0.0", port=5000)