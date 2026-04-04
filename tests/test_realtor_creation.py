from app import app, init_db


def test_can_add_realtor():
    init_db()

    client = app.test_client()
    response = client.post(
        "/realtors",
        data={
            "first_name": "Jake",
            "last_name": "Kistler",
            "email": "jake@example.com",
            "phone": "555-111-2222",
            "brokerage": "Example Realty",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Jake" in response.data
    assert b"Kistler" in response.data
    assert b"jake@example.com" in response.data