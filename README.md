
# Backend

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

# Frontend

```sh
cd frontend
npm install
npm run dev
```

# Code policy

## Core principles (FastAPI + SQLAlchemy)

FastAPI expects:

- One Engine per application
- One Session per request
- Explicit session close
- No global sessions
- No ORM usage outside a session scope

This is non-negotiable if you want predictable behavior.


## Pydantic schemas policy

Define **Pydantic** schemas that mirror your API, not your DB.

