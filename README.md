
# Backend

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```
# VueJS Frontend

to be implemented

# Textual Frontend

While in development:

```sh
cd textualfrontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
textual run --dev main.py
```

Run:

```sh
cd textualfrontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

# Alpine Frontend

The current Alpine frontend is not built, the JS dependencies are included in a *script* tag.

To run the frontend, you just have to serve the files in the folder using a web server. For
example:

```sh
python3 -m http.server 8080
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

