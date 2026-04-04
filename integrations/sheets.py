import os


def is_configured() -> bool:
    file_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    spreadsheet_id = os.environ.get("GOOGLE_SPREADSHEET_ID")
    return bool(file_path and os.path.isfile(file_path) and spreadsheet_id)


def export_referrals(get_db_connection) -> dict:
    """
    Read all referrals + payout info from SQLite and write to a Google Sheet.

    Returns:
        {
            "status": "ok" | "not_configured" | "error",
            "rows_written": int,
            "sheet_url": str | None,
            "message": str,
        }
    """
    if not is_configured():
        return {
            "status": "not_configured",
            "rows_written": 0,
            "sheet_url": None,
            "message": "Google Sheets credentials are not configured.",
        }

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        return {
            "status": "error",
            "rows_written": 0,
            "sheet_url": None,
            "message": "gspread or google-auth library not installed.",
        }

    # Spreadsheets scope only — no Drive access needed since the sheet is pre-created
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    try:
        creds = Credentials.from_service_account_file(
            os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"],
            scopes=SCOPES,
        )
        client = gspread.authorize(creds)
    except Exception as exc:
        return {
            "status": "error",
            "rows_written": 0,
            "sheet_url": None,
            "message": f"Google auth failed: {exc}",
        }

    spreadsheet_id = os.environ["GOOGLE_SPREADSHEET_ID"]
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1
    except gspread.SpreadsheetNotFound:
        service_account_email = "unknown"
        try:
            import json
            with open(os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"]) as f:
                service_account_email = json.load(f).get("client_email", "unknown")
        except Exception:
            pass
        return {
            "status": "error",
            "rows_written": 0,
            "sheet_url": None,
            "message": (
                f"Spreadsheet not found. Make sure you have shared it (Editor access) "
                f"with the service account: {service_account_email}"
            ),
        }

    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                re.first_name || ' ' || re.last_name  AS referring_realtor,
                rf.referred_first_name || ' ' || rf.referred_last_name AS referred_person,
                rf.referral_date,
                rf.status                              AS referral_status,
                COALESCE(p.amount, '')                 AS payout_amount,
                COALESCE(p.status, 'N/A')              AS payout_status,
                COALESCE(p.paid_at, '')                AS paid_at
            FROM referrals AS rf
            JOIN realtors AS re ON rf.referring_realtor_id = re.id
            LEFT JOIN payouts AS p ON p.referral_id = rf.id
            ORDER BY rf.referral_date DESC, rf.id DESC
            """
        ).fetchall()
    finally:
        conn.close()

    header = [
        "Referring Realtor",
        "Referred Person",
        "Referral Date",
        "Referral Status",
        "Payout Amount",
        "Payout Status",
        "Paid At",
    ]
    data = [header] + [list(row) for row in rows]

    try:
        worksheet.clear()
        worksheet.update("A1", data)
    except Exception as exc:
        return {
            "status": "error",
            "rows_written": 0,
            "sheet_url": None,
            "message": f"Failed to write to sheet: {exc}",
        }

    return {
        "status": "ok",
        "rows_written": len(rows),
        "sheet_url": spreadsheet.url,
        "message": f"Export complete. {len(rows)} rows written.",
    }
