import os
import sqlite3


def is_configured() -> bool:
    # Requires username, client ID, and either a key file path or inline key string
    has_key = (
        os.environ.get("SF_PRIVATE_KEY_FILE")
        or os.environ.get("SF_PRIVATE_KEY")
    )
    return bool(
        os.environ.get("SF_USERNAME")
        and os.environ.get("SF_CLIENT_ID")
        and has_key
    )


def import_realtors(get_db_connection) -> dict:
    """
    Connect to Salesforce, query Contacts, upsert into realtors table.

    Returns:
        {
            "status": "ok" | "not_configured" | "error",
            "imported": int,
            "skipped": int,
            "errors": list[str],
            "message": str,
        }
    """
    if not is_configured():
        return {
            "status": "not_configured",
            "imported": 0,
            "skipped": 0,
            "errors": [],
            "message": "Salesforce credentials are not configured.",
        }

    try:
        from simple_salesforce import Salesforce  # noqa: PLC0415
    except ImportError:
        return {
            "status": "error",
            "imported": 0,
            "skipped": 0,
            "errors": ["simple-salesforce library not installed."],
            "message": "Library missing.",
        }

    # Build JWT auth kwargs — prefer key file, fall back to inline key string
    auth_kwargs = {
        "username": os.environ["SF_USERNAME"],
        "consumer_key": os.environ["SF_CLIENT_ID"],
        "domain": os.environ.get("SF_DOMAIN", "login"),
    }
    if os.environ.get("SF_PRIVATE_KEY_FILE"):
        auth_kwargs["privatekey_file"] = os.environ["SF_PRIVATE_KEY_FILE"]
    else:
        auth_kwargs["privatekey"] = os.environ["SF_PRIVATE_KEY"]

    try:
        sf = Salesforce(**auth_kwargs)
    except Exception as exc:
        return {
            "status": "error",
            "imported": 0,
            "skipped": 0,
            "errors": [str(exc)],
            "message": "Failed to connect to Salesforce.",
        }

    soql = (
        "SELECT Id, FirstName, LastName, Email, MobilePhone, Account.Name "
        "FROM Contact "
        "WHERE Email != null AND Contact_Type__c = 'Realtor' "
        "ORDER BY LastName, FirstName "
        "LIMIT 1000"
    )

    try:
        result = sf.query_all(soql)
    except Exception as exc:
        return {
            "status": "error",
            "imported": 0,
            "skipped": 0,
            "errors": [str(exc)],
            "message": "Salesforce query failed.",
        }

    records = result.get("records", [])
    imported = 0
    skipped = 0
    per_record_errors = []

    conn = get_db_connection()
    try:
        for rec in records:
            first_name = rec.get("FirstName") or ""
            last_name  = rec.get("LastName") or ""
            email      = rec.get("Email") or ""
            phone      = rec.get("MobilePhone") or ""
            account    = rec.get("Account") or {}
            brokerage  = account.get("Name") or "" if isinstance(account, dict) else ""

            if not email:
                per_record_errors.append(f"Skipping record {rec.get('Id')}: no email.")
                skipped += 1
                continue

            try:
                conn.execute(
                    """
                    INSERT INTO realtors (first_name, last_name, email, phone, brokerage)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (first_name, last_name, email, phone, brokerage),
                )
                conn.commit()
                imported += 1
            except sqlite3.IntegrityError:
                skipped += 1
    finally:
        conn.close()

    return {
        "status": "ok",
        "imported": imported,
        "skipped": skipped,
        "errors": per_record_errors,
        "message": f"Import complete. {imported} imported, {skipped} skipped.",
    }
