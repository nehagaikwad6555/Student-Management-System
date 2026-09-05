from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Neha@2101",
        database="student_management"
    )


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
        cursor = db.cursor()

        query = """
        INSERT INTO students (name, email, phone, course, department)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (name, email, phone, course, department)
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect("/")

    return render_template("add_student.html")


@app.route("/view")
def view_students():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("view_students.html", students=students)


@app.route("/delete/<int:id>")
def delete_student(id):
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = %s",
        (id,)
    )

    db.commit()
    cursor.close()
    db.close()

    return redirect("/view")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]
        department = request.form["department"]

        query = """
        UPDATE students
        SET name=%s,
            email=%s,
            phone=%s,
            course=%s,
            department=%s
        WHERE id=%s
        """

        cursor.execute(
            query,
            (name, email, phone, course, department, id)
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect("/view")

    cursor.execute(
        "SELECT * FROM students WHERE id=%s",
        (id,)
    )

    student = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "edit_student.html",
        student=student
    )


@app.route("/search")
def search_student():
    name = request.args.get("name", "")

    db = get_db_connection()
    cursor = db.cursor()

    query = "SELECT * FROM students WHERE name LIKE %s"
    cursor.execute(query, ("%" + name + "%",))

    students = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "view_students.html",
        students=students
    )


if __name__ == "__main__":
    app.run(debug=True)