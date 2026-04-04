from app import app, init_db, get_db_connection


def test_qualifying_referral_creates_payout():
    init_db()

    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO realtors (first_name, last_name, email, phone, brokerage)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("Jake", "Kistler", "jake@example.com", "555-111-2222", "Example Realty"),
    )
    conn.commit()

    realtor = conn.execute(
        "SELECT id FROM realtors WHERE email = ?",
        ("jake@example.com",),
    ).fetchone()

    conn.execute(
        """
        INSERT INTO referrals (
            referring_realtor_id,
            referred_first_name,
            referred_last_name,
            referred_email,
            referred_phone,
            referral_date,
            status,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            realtor["id"],
            "Darci",
            "Kistler",
            "darci@example.com",
            "4053232320",
            "2026-04-03",
            "pending",
            "Test referral",
        ),
    )
    conn.commit()

    referral = conn.execute(
        "SELECT id FROM referrals WHERE referred_email = ?",
        ("darci@example.com",),
    ).fetchone()
    conn.close()

    client = app.test_client()
    response = client.post(
        f"/referrals/{referral['id']}/qualify",
        follow_redirects=True,
    )

    assert response.status_code == 200

    conn = get_db_connection()

    updated_referral = conn.execute(
        "SELECT status FROM referrals WHERE id = ?",
        (referral["id"],),
    ).fetchone()

    payout = conn.execute(
        """
        SELECT referral_id, payee_realtor_id, amount, status
        FROM payouts
        WHERE referral_id = ?
        """,
        (referral["id"],),
    ).fetchone()

    conn.close()

    assert updated_referral["status"] == "qualified"
    assert payout is not None
    assert payout["referral_id"] == referral["id"]
    assert payout["payee_realtor_id"] == realtor["id"]
    assert payout["amount"] == 250.0
    assert payout["status"] == "pending"

def test_payouts_page_loads():
    init_db()

    client = app.test_client()
    response = client.get("/payouts")

    assert response.status_code == 200
    assert b"Payouts" in response.data