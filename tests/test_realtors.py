from app import app

def test_realtors_page_loads():
    client = app.test_client()
    response = client.get("/realtors")

    assert response.status_code == 200