import shutil
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException

from db.engine import DATABASE_URL

router = APIRouter()


@router.post("/", status_code=201)
def backup_database():
    """Copy the SQLite database file to a timestamped .bak file."""
    # DATABASE_URL is "sqlite:///./portfolio.db"
    db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
    if not db_path.exists():
        raise HTTPException(status_code=404, detail=f"Database file not found: {db_path}")

    timestamp = datetime.now().strftime("%Y.%m.%d.%H.%M")
    backup_path = db_path.parent / f"{db_path.name}.{timestamp}.bak"

    shutil.copy2(db_path, backup_path)
    return {"backup": str(backup_path)}
