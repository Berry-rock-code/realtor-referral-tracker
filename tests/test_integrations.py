import sqlite3
import pytest
from integrations.salesforce import is_configured as sf_configured, import_realtors
from integrations.sheets import is_configured as sheets_configured, export_referrals
from app import app as flask_app


def make_empty_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    return conn


# --- Salesforce: configuration checks ---

def test_sf_not_configured_when_env_missing(monkeypatch):
    for var in ["SF_USERNAME", "SF_CLIENT_ID", "SF_PRIVATE_KEY_FILE", "SF_PRIVATE_KEY"]:
        monkeypatch.delenv(var, raising=False)
    assert sf_configured() is False


def test_sf_configured_when_all_env_set(monkeypatch):
    monkeypatch.setenv("SF_USERNAME", "u")
    monkeypatch.setenv("SF_CLIENT_ID", "client_id")
    monkeypatch.setenv("SF_PRIVATE_KEY", "fake_key")
    assert sf_configured() is True


def test_sf_import_returns_not_configured_without_env(monkeypatch):
    for var in ["SF_USERNAME", "SF_CLIENT_ID", "SF_PRIVATE_KEY_FILE", "SF_PRIVATE_KEY"]:
        monkeypatch.delenv(var, raising=False)
    result = import_realtors(make_empty_db)
    assert result["status"] == "not_configured"
    assert result["imported"] == 0


# --- Sheets: configuration checks ---

def test_sheets_not_configured_when_env_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_SPREADSHEET_ID", raising=False)
    assert sheets_configured() is False


def test_sheets_not_configured_when_file_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(tmp_path / "nonexistent.json"))
    monkeypatch.setenv("GOOGLE_SPREADSHEET_ID", "fake_id")
    assert sheets_configured() is False


def test_sheets_export_returns_not_configured_without_env(monkeypatch):
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_SPREADSHEET_ID", raising=False)
    result = export_referrals(make_empty_db)
    assert result["status"] == "not_configured"
    assert result["sheet_url"] is None


# --- Route-level: pages load and degrade gracefully without credentials ---

def test_import_salesforce_get_loads(monkeypatch):
    for var in ["SF_USERNAME", "SF_CLIENT_ID", "SF_PRIVATE_KEY_FILE", "SF_PRIVATE_KEY"]:
        monkeypatch.delenv(var, raising=False)
    response = flask_app.test_client().get("/import/salesforce")
    assert response.status_code == 200
    assert b"Not configured" in response.data


def test_export_sheets_get_loads(monkeypatch):
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_SPREADSHEET_ID", raising=False)
    response = flask_app.test_client().get("/export/sheets")
    assert response.status_code == 200
    assert b"Not configured" in response.data


def test_import_salesforce_post_without_creds(monkeypatch):
    for var in ["SF_USERNAME", "SF_CLIENT_ID", "SF_PRIVATE_KEY_FILE", "SF_PRIVATE_KEY"]:
        monkeypatch.delenv(var, raising=False)
    response = flask_app.test_client().post("/import/salesforce")
    assert response.status_code == 200
    assert b"not_configured" in response.data


def test_export_sheets_post_without_creds(monkeypatch):
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_SPREADSHEET_ID", raising=False)
    response = flask_app.test_client().post("/export/sheets")
    assert response.status_code == 200
    assert b"not_configured" in response.data
