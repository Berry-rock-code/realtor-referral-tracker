import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config["DATABASE"] = "referral_tracker.db"
PAYOUT_AMOUNT = 250.0

def get_db_connection():
    conn = sqlite3.connect(app.config["DATABASE"])
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

    realtor_rows = conn.execute(
        """
        SELECT
            re.id,
            re.first_name,
            re.last_name,
            re.email,
            re.phone,
            re.brokerage,
            refr.first_name || ' ' || refr.last_name AS referred_by,
            COALESCE(SUM(CASE WHEN p.status = 'paid' THEN p.amount ELSE 0 END), 0) AS total_paid,
            COUNT(DISTINCT outgoing.id) AS referrals_made
        FROM realtors re
        LEFT JOIN referrals incoming ON incoming.referred_email = re.email
        LEFT JOIN realtors refr ON incoming.referring_realtor_id = refr.id
        LEFT JOIN referrals outgoing ON outgoing.referring_realtor_id = re.id
        LEFT JOIN payouts p ON p.payee_realtor_id = re.id
        GROUP BY re.id, re.first_name, re.last_name, re.email, re.phone, re.brokerage, referred_by
        ORDER BY re.id DESC
        """
    ).fetchall()
    conn.close()

    return render_template("realtors.html", realtors=realtor_rows)

@app.route("/realtors/<int:realtor_id>/update-brokerage", methods=["POST"])
def update_brokerage(realtor_id):
    brokerage = request.form["brokerage"]
    conn = get_db_connection()
    conn.execute(
        "UPDATE realtors SET brokerage = ? WHERE id = ?",
        (brokerage, realtor_id),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("realtors"))


@app.route("/referrals", methods=["GET", "POST"])
def referrals():
    conn = get_db_connection()

    if request.method == "POST":
        referring_realtor_id = request.form["referring_realtor_id"]
        referred_first_name = request.form["referred_first_name"]
        referred_last_name = request.form["referred_last_name"]
        referred_email = request.form["referred_email"]
        referred_phone = request.form["referred_phone"]
        referral_date = request.form["referral_date"]
        notes = request.form["notes"]

        existing = conn.execute(
            "SELECT id FROM referrals WHERE referred_email = ?",
            (referred_email,),
        ).fetchone()

        if existing:
            realtor_rows = conn.execute(
                "SELECT id, first_name, last_name FROM realtors ORDER BY last_name, first_name"
            ).fetchall()
            referral_rows = conn.execute(
                """
                SELECT
                    referrals.id,
                    referrals.referred_first_name,
                    referrals.referred_last_name,
                    referrals.referred_email,
                    referrals.referred_phone,
                    referrals.referral_date,
                    referrals.status,
                    referrals.notes,
                    realtors.first_name AS referring_first_name,
                    realtors.last_name AS referring_last_name
                FROM referrals
                JOIN realtors ON referrals.referring_realtor_id = realtors.id
                ORDER BY referrals.id DESC
                """
            ).fetchall()
            conn.close()
            return render_template(
                "referrals.html",
                realtors=realtor_rows,
                referrals=referral_rows,
                error=f"{referred_email} has already been referred.",
            )

        conn.execute(
            """
            INSERT INTO referrals (
                referring_realtor_id,
                referred_first_name,
                referred_last_name,
                referred_email,
                referred_phone,
                referral_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                referring_realtor_id,
                referred_first_name,
                referred_last_name,
                referred_email,
                referred_phone,
                referral_date,
                notes,
            ),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("referrals"))

    realtor_rows = conn.execute(
        "SELECT id, first_name, last_name FROM realtors ORDER BY last_name, first_name"
    ).fetchall()

    referral_rows = conn.execute(
        """
        SELECT
            referrals.id,
            referrals.referred_first_name,
            referrals.referred_last_name,
            referrals.referred_email,
            referrals.referred_phone,
            referrals.referral_date,
            referrals.status,
            referrals.notes,
            realtors.first_name AS referring_first_name,
            realtors.last_name AS referring_last_name
        FROM referrals
        JOIN realtors
            ON referrals.referring_realtor_id = realtors.id
        ORDER BY referrals.id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "referrals.html",
        realtors=realtor_rows,
        referrals=referral_rows,
        error=None,
    )

@app.route("/referrals/<int:referral_id>/qualify", methods=["POST"])
def qualify_referral(referral_id):
    conn = get_db_connection()

    referral = conn.execute(
        """
        SELECT id, referring_realtor_id, status,
               referred_first_name, referred_last_name,
               referred_email, referred_phone
        FROM referrals
        WHERE id = ?
        """,
        (referral_id,),
    ).fetchone()

    if referral is None:
        conn.close()
        return "Referral not found", 404

    if referral["status"] != "pending":
        conn.close()
        return redirect(url_for("referrals"))

    conn.execute(
        "UPDATE referrals SET status = 'qualified' WHERE id = ?",
        (referral_id,),
    )

    conn.execute(
        """
        INSERT INTO payouts (referral_id, payee_realtor_id, amount, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            referral["id"],
            referral["referring_realtor_id"],
            PAYOUT_AMOUNT,
            "pending",
        ),
    )

    # Promote the referred person to a realtor so they can refer others
    try:
        conn.execute(
            """
            INSERT INTO realtors (first_name, last_name, email, phone)
            VALUES (?, ?, ?, ?)
            """,
            (
                referral["referred_first_name"],
                referral["referred_last_name"],
                referral["referred_email"],
                referral["referred_phone"],
            ),
        )
    except sqlite3.IntegrityError:
        pass  # Already exists in realtors — no action needed

    conn.commit()
    conn.close()

    return redirect(url_for("referrals"))

@app.route("/payouts/<int:payout_id>/mark-paid", methods=["POST"])
def mark_payout_paid(payout_id):
    conn = get_db_connection()

    payout = conn.execute(
        "SELECT id, status FROM payouts WHERE id = ?",
        (payout_id,),
    ).fetchone()

    if payout is None:
        conn.close()
        return "Payout not found", 404

    if payout["status"] != "pending":
        conn.close()
        return redirect(url_for("payouts"))

    conn.execute(
        """
        UPDATE payouts
        SET status = 'paid', paid_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (payout_id,),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("payouts"))


@app.route("/payouts")
def payouts():
    conn = get_db_connection()

    payout_rows = conn.execute(
        """
        SELECT
            p.id,
            p.amount,
            p.status,
            p.created_at,
            p.paid_at,
            r.referred_first_name,
            r.referred_last_name,
            r.referred_email,
            re.first_name AS payee_first_name,
            re.last_name AS payee_last_name
        FROM payouts AS p
        JOIN referrals AS r
            ON p.referral_id = r.id
        JOIN realtors AS re
            ON p.payee_realtor_id = re.id
        ORDER BY p.id DESC
        """
    ).fetchall()

    totals_rows = conn.execute(
        """
        SELECT
            re.first_name || ' ' || re.last_name AS realtor_name,
            SUM(CASE WHEN p.status = 'paid' THEN p.amount ELSE 0 END) AS total_paid,
            SUM(CASE WHEN p.status = 'pending' THEN p.amount ELSE 0 END) AS total_pending,
            COUNT(*) AS payout_count
        FROM payouts p
        JOIN realtors re ON p.payee_realtor_id = re.id
        GROUP BY re.id
        ORDER BY total_paid DESC
        """
    ).fetchall()

    conn.close()

    return render_template("payouts.html", payouts=payout_rows, totals=totals_rows)


if __name__ == "__main__":
    app.run(debug=True)