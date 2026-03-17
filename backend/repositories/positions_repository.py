from sqlalchemy import select
from sqlalchemy.orm import Session
from db.models import Position
import logging

log = logging.getLogger(__name__)

def get_all_positions(session: Session, account_id: int = None):
    stmt = select(Position)
    if account_id:
        stmt = stmt.filter_by(account_id=account_id)
    return session.scalars(stmt).all()

def delete_position(session: Session, position_id: int) -> bool:
    position = session.get(Position, position_id)
    if position:
        try:
            session.delete(position)
            session.commit()
            log.info(f"🗑️ Deleted Position ID {position_id}")
            return True
        except Exception as e:
            session.rollback()
            log.error(f"⚠️ Cannot delete Position ID {position_id}: {e}")
            return False
    else:
        log.warning(f"⚠️ Position ID {position_id} not found.")
        return False
