import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATABASE = "referral_tracker.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with open("schema.sql", "r", encoding="utf-8") as file:
        sql_script = file.read()
    
    conn = get_db_connection()
    conn.executescript(sql_script)
    conn.close()

@app.route("/")
def index():
    conn = get_db_connection()

    realtor_count = conn.execute(
        "SELECT COUNT(*) AS count FROM realtors"
    ).fetchone()["count"]

    referral_count = conn.execute(
        "SELECT COUNT(*) AS count FROM referrals"
    ).fetchone()["count"]

    payout_count = conn.execute(
        "SELECT COUNT(*) AS count FROM payouts"
    ).fetchone()["count"]

    conn.close()

    return render_template(
        "index.html",
        realtor_count=realtor_count,
        referral_count=referral_count,
        payout_count=payout_count
    )

@app.route("/init-db")
def initialize_database():
    init_db()
    return "Database initialized."

@app.route("/realtors", methods=["GET", "POST"])
def realtors():
    conn = get_db_connection()

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        brokerage = request.form["brokerage"]

        conn.execute(
            """
            INSERT INTO realtors (first_name, last_name, email, phone, brokerage)
            VALUES (?, ?, ?, ?, ?)
            """,
            (first_name, last_name, email, phone, brokerage),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("realtors"))

    realtor_rows = conn.execute("SELECT * FROM realtors ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("realtors.html", realtors=realtor_rows)


if __name__ == "__main__":
    app.run(debug=True)