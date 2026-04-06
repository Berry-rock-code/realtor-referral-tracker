# Realtor Referral Tracker

A lightweight internal tool for tracking realtor-to-realtor referrals and payout obligations. Built as an MVP prototype to validate the workflow and data model before investing in a production system.

---

## Demo

A full walkthrough video is included in the repo: `MVP_DEMO.mp4`

---

## What It Does

- Add realtors and track their brokerage  
- Record referrals between realtors  
- Qualify a referral — auto-creates a $250 payout and promotes the referred person to a realtor  
- Mark payouts as paid  
- See who referred who, referrals made, and total earned per realtor  
- Duplicate referral protection — the same person cannot be referred twice  
- Dashboard with live counts across all three tables  

---

## Tech Stack

| Layer | Technology |
|------|------------|
| Web framework | Flask (Python) |
| Database | SQLite |
| Templates | Jinja2 (server-rendered HTML) |
| Tests | pytest |
| Code quality | Black + Ruff |

---

## Project Structure

```
realtor-referral-tracker/
├── app.py
├── schema.sql
├── requirements.txt
├── MVP_DEMO.mp4
├── PROJECT_OVERVIEW.md
├── templates/
│   ├── index.html
│   ├── realtors.html
│   ├── referrals.html
│   └── payouts.html
└── tests/
    ├── conftest.py
    ├── test_app.py
    ├── test_realtors.py
    ├── test_realtor_creation.py
    ├── test_referrals.py
    └── test_payouts.py
```

---

## Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python -c "from app import init_db; init_db()"

# Start the server
flask --app app run
```

---

## Pages

| Route | Purpose |
|------|--------|
| / | Dashboard — live counts |
| /realtors | Add realtors, view list with referred-by and earnings |
| /referrals | Add referrals, qualify pending referrals |
| /payouts | View payouts, mark as paid, per-realtor totals |

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use isolated temp databases and are safe to run while the server is running.

---

## Why Not Just Use Google Sheets?

While a spreadsheet-based approach is familiar and easy to start with, this system intentionally uses a relational database to solve problems that spreadsheets handle poorly as complexity grows.

### 1. Relationship Integrity

This system tracks relationships between entities:

- A realtor refers another realtor  
- A referral may generate a payout  
- A payout must be tied to exactly one referral  

A relational database enforces these relationships explicitly through foreign keys and constraints, ensuring the data remains consistent.

---

### 2. Prevention of Duplicate and Invalid Data

The system enforces important business rules:

- A referred person can only be referred once  
- A referral can only generate one payout  
- A payout cannot be paid twice  

In a spreadsheet, enforcing these rules requires manual vigilance or fragile formulas. A database enforces these rules automatically.

---

### 3. Workflow State Management

The system models a real workflow:

Referral → Qualified → Payout Created → Paid

Each action has downstream effects. The application ensures these transitions happen correctly and prevents invalid states.

---

### 4. Auditability and Reliability

Because payouts involve money, it is important to track:

- who referred whom  
- when a referral was qualified  
- whether a payout has been paid  

A database provides a reliable, structured source of truth, reducing the risk of accidental overwrites or inconsistencies.

---

### 5. Scalability and Future Integration

This MVP is designed for future expansion:

- Salesforce integration  
- Google Sheets export for reporting  
- Cloud deployment  

A database-backed system provides a scalable foundation, while spreadsheets can still be used as a reporting layer.

---

### 6. Separation of Concerns

- Database → data integrity  
- Application → business logic  
- UI → user interaction  

Spreadsheets combine all three, which leads to fragile systems and harder maintenance.

---

## Summary

A spreadsheet is useful for quick tracking, but this system requires:

- reliable relationships  
- enforced business rules  
- controlled workflows  
- accurate payout tracking  

For these reasons, a database-backed application is the appropriate foundation.

---

## Next Steps (Post-MVP)

- Salesforce realtor import (scaffolding planned)  
- Google Sheets export for reporting  
- Cloud deployment (PostgreSQL + hosted app)  
- Authentication and user accounts  
- Configurable payout amounts  
- Email notifications  
