import pytest
from app import app as flask_app, init_db


@pytest.fixture(autouse=True)
def isolated_db(tmp_path):
    """Give every test its own temp database so the live server never interferes."""
    db_path = str(tmp_path / "test.db")
    flask_app.config["DATABASE"] = db_path
    init_db()
    yield
    flask_app.config["DATABASE"] = "referral_tracker.db"
