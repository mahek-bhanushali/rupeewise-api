# RUPEEWISE API

A REST API built with **Flask**, **SQLAlchemy** and **SQLite** for tracking personal expenses.
Users register, log in (JWT token), and manage their own expenses with filtering,
pagination and a spending summary.

## Features

* User registration and login with hashed passwords and JWT authentication
* Full CRUD for expenses (each user can only see their own data)
* Filter by category and date range, with pagination
* Summary endpoint: total spent and totals per category
* Input validation and consistent JSON error responses
* Layered structure: routes (HTTP) -> services (business logic) -> models (database)
* 15 automated tests with pytest

## Tech stack

Python 3, Flask, Flask-SQLAlchemy, SQLite, PyJWT, pytest, gunicorn

## Project structure

```
rupeewise-api/
├── app/
│   ├── \\\_\\\_init\\\_\\\_.py          # application factory + error handlers
│   ├── extensions.py        # db instance
│   ├── models.py            # User, Expense
│   ├── auth\\\_utils.py        # JWT creation + token\\\_required decorator
│   ├── routes/              # auth.py, expenses.py (HTTP layer)
│   └── services/            # expense\\\_service.py (business logic + validation)
├── tests/                   # pytest tests
├── config.py
├── run.py
└── requirements.txt
```

## Setup

```bash
git clone https://github.com/mahek-bhanushali/rupeewise-api.git
cd rupeewise-api
python -m venv venv
venv\\\\Scripts\\\\activate        # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python run.py
```

The API runs at http://127.0.0.1:5000

Set `SECRET\\\_KEY` as an environment variable in production.

## Run tests

```bash
pytest -v
```

## API endpoints

|Method|Endpoint|Auth|Description|
|-|-|-|-|
|POST|`/api/auth/register`|No|Create account|
|POST|`/api/auth/login`|No|Get JWT token|
|POST|`/api/expenses`|Yes|Add expense|
|GET|`/api/expenses`|Yes|List expenses (`category`, `start`, `end`, `page`, `per\\\_page`)|
|GET|`/api/expenses/<id>`|Yes|Get one expense|
|PUT|`/api/expenses/<id>`|Yes|Update expense|
|DELETE|`/api/expenses/<id>`|Yes|Delete expense|
|GET|`/api/expenses/summary`|Yes|Total and per-category summary|

Send the token as: `Authorization: Bearer <token>`

### Example usage

```bash
# Register and log in
curl -X POST http://127.0.0.1:5000/api/auth/register -H "Content-Type: application/json" \\\\
  -d '{"username":"mahek","password":"secret123"}'
curl -X POST http://127.0.0.1:5000/api/auth/login -H "Content-Type: application/json" \\\\
  -d '{"username":"mahek","password":"secret123"}'

# Add an expense
curl -X POST http://127.0.0.1:5000/api/expenses \\\\
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \\\\
  -d '{"title":"Lunch","amount":150,"category":"food","date":"2026-11-23"}'

# Filter
curl "http://127.0.0.1:5000/api/expenses?category=food\\\&start=2026-11-01\\\&end=2026-11-30" \\\\
  -H "Authorization: Bearer <token>"
```

Expense JSON fields: `title` (required), `amount` (required, > 0), `category`, `date` (YYYY-MM-DD), `note`.

## Deployment 

* Build command: `pip install -r requirements.txt`
* Start command: `gunicorn run:app`
* Environment variable: `SECRET\\\_KEY`

## Possible improvements

* Switch to PostgreSQL, add Flask-Migrate for database migrations
* Add monthly budget limits and CSV export

