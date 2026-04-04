import sqlite3
from flask import Flask, render_template

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

if __name__ == "__main__":
    app.run(debug=True)