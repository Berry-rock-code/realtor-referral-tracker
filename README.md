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
| --- | --- |
| Web framework | Flask (Python) |
| Database | SQLite |
| Templates | Jinja2 (server-rendered HTML) |
| Tests | pytest |
| Code quality | Black + Ruff |

---

## Project Structure

```
realtor-referral-tracker/
├── app.py                  # All routes and business logic
├── schema.sql              # Database schema (realtors, referrals, payouts)
├── requirements.txt
├── MVP_DEMO.mp4            # Demo walkthrough video
├── PROJECT_OVERVIEW.md     # Data flow diagrams and full demo walkthrough doc
├── templates/
│   ├── index.html          # Dashboard
│   ├── realtors.html       # Realtor list + add form
│   ├── referrals.html      # Referral list + add form + qualify
│   └── payouts.html        # Payout list + mark as paid + totals
└── tests/
    ├── conftest.py         # Isolated temp DB per test
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
| --- | --- |
| `/` | Dashboard — live counts |
| `/realtors` | Add realtors, view list with referred-by and earnings |
| `/referrals` | Add referrals, qualify pending referrals |
| `/payouts` | View payouts, mark as paid, per-realtor totals |

---

## Running Tests

Tests use isolated temp databases and are safe to run while the server is running.

```bash
pytest tests/ -v
```

---

## Next Steps (Post-MVP)

- Salesforce realtor import (scaffolding planned)
- Google Sheets export for quick reporting (scaffolding planned)
- Cloud deployment (PostgreSQL + hosted app)
- Authentication and user accounts
- Configurable payout amounts
- Email notifications on qualification or payout
