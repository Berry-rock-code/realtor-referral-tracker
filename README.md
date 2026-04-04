# Realtor Referral Tracker

## Overview

This project is a prototype internal tool for tracking realtor-to-realtor referrals and associated payout obligations.

The goal of this MVP is to validate:
- the referral workflow
- the underlying data model
- the usability of a database-backed system vs spreadsheets

---

## Features (MVP)

- Add and view realtors
- Create and view referrals
- Link referrals to existing realtors
- Track referral status (default: `pending`)
- Relational data using SQLite
- Basic automated tests using pytest

---

## Tech Stack

- Python
- Flask
- SQLite
- Jinja (server-rendered HTML)
- pytest (testing)
- Black (formatter)
- Ruff (linter)

---

## Project Structure

realtor-referral-tracker/
├── app.py
├── schema.sql
├── requirements.txt
├── README.md
├── templates/
├── static/
└── tests/

---

## Setup

### 1. Create virtual environment

python3 -m venv .venv
source .venv/bin/activate

### 2. Install dependencies

pip install -r requirements.txt

---

## Running the App

python app.py

Then open:

http://127.0.0.1:5000

---

## Initialize Database

Before using the app, initialize the database:

http://127.0.0.1:5000/init-db

---

## Running Tests

pytest -v

---

## Current Workflow

1. Create a realtor
2. Create a referral linked to that realtor
3. View referrals and associated data

---

## Next Steps

- Add "qualify referral" action
- Automatically generate payouts
- Add payouts page and tracking
- Improve test isolation (temporary DB)
- Introduce navigation and UI cleanup
- Explore future cloud deployment

---

## Notes

This project is currently a prototype and is intentionally minimal to allow rapid iteration and validation of business logic.
