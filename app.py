from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return redirect("/add-employee")


@app.route("/add-employee", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO employees (name, email, department) VALUES (?, ?, ?)",
            (name, email, department)
        )

        conn.commit()
        conn.close()

        return "Employee added successfully!"

    return render_template("add_employee.html")


@app.route("/employees")
def employees():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()

    conn.close()

    return render_template("employees.html", employees=employees)


@app.route("/apply-leave", methods=["GET", "POST"])
@app.route("/apply-leave", methods=["GET", "POST"])
def apply_leave():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        employee_id = request.form["employee_id"]
        leave_type = request.form["leave_type"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        reason = request.form["reason"]

        cursor.execute("""
            INSERT INTO leave_requests
            (employee_id, leave_type, start_date, end_date, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (
            employee_id,
            leave_type,
            start_date,
            end_date,
            reason
        ))

        conn.commit()
        conn.close()

        return "Leave applied successfully!"

    cursor.execute("SELECT id, name FROM employees")
    employees = cursor.fetchall()

    conn.close()

    return render_template(
        "apply_leave.html",
        employees=employees
    )


@app.route("/leave-requests")
def leave_requests():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leave_requests")
    leaves = cursor.fetchall()

    conn.close()

    return render_template("leave_requests.html", leaves=leaves)


@app.route("/approve-leave/<int:leave_id>")
def approve_leave(leave_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE leave_requests SET status = 'Approved' WHERE id = ?",
        (leave_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/leave-requests")


@app.route("/reject-leave/<int:leave_id>")
def reject_leave(leave_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE leave_requests SET status = 'Rejected' WHERE id = ?",
        (leave_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/leave-requests")
@app.route("/delete-employee/<int:employee_id>")
def delete_employee(employee_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Pehle employee ki leave requests delete karna
    cursor.execute(
        "DELETE FROM leave_requests WHERE employee_id = ?",
        (employee_id,)
    )

    # Employee delete karna
    cursor.execute(
        "DELETE FROM employees WHERE id = ?",
        (employee_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/employees")

@app.route("/edit-employee/<int:employee_id>", methods=["GET", "POST"])
def edit_employee(employee_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]

        cursor.execute("""
            UPDATE employees
            SET name = ?, email = ?, department = ?
            WHERE id = ?
        """, (name, email, department, employee_id))

        conn.commit()
        conn.close()

        return redirect("/employees")

    cursor.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,)
    )

    employee = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_employee.html",
        employee=employee
    )

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leave_requests")
    total_leaves = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM leave_requests WHERE status = 'Pending'"
    )
    pending_leaves = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM leave_requests WHERE status = 'Approved'"
    )
    approved_leaves = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM leave_requests WHERE status = 'Rejected'"
    )
    rejected_leaves = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_employees=total_employees,
        total_leaves=total_leaves,
        pending_leaves=pending_leaves,
        approved_leaves=approved_leaves,
        rejected_leaves=rejected_leaves
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)