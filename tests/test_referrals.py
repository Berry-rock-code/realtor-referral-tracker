from app import app, init_db, get_db_connection

def test_referrals_page_loads():
    init_db()

    client = app.test_client()
    response = client.get("/referrals")

    assert response.status_code == 200
    assert b"Referrals" in response.data

def test_can_add_referral():
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
    conn.close()

    client = app.test_client()
    response = client.post(
        "/referrals",
        data={
            "referring_realtor_id": realtor["id"],
            "referred_first_name": "Darci",
            "referred_last_name": "Kistler",
            "referred_email": "darci@example.com",
            "referred_phone": "555-333-4444",
            "referral_date": "2026-04-04",
            "notes": "Test referral",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    conn = get_db_connection()
    referral = conn.execute(
        "SELECT * FROM referrals WHERE referred_email = ?",
        ("darci@example.com",),
    ).fetchone()
    conn.close()

    assert referral is not None
    assert referral["referred_first_name"] == "Darci"
    assert referral["referring_realtor_id"] == realtor["id"]
    assert referral["status"] == "pending"