
from sqlalchemy import select
from lib.models import Position
from logging_config import setup_logger
log = setup_logger(__name__)


def get_all_positions(session, account=None):

    stmt = select(Position)
    if account:
        stmt = stmt.filter_by(account_id=account.id)
    return session.scalars(stmt).all()

def get_position_by_id(session, position_id):
    return session.get(Position, position_id)

def close_position(session, position, closing_date):
    position.closed = True
    position.closing_date = closing_date
    session.flush()
    log.info(f"🔒 Closed Position ID {position.id}")

def delete_position(session, position_id):
    position = session.get(Position, position_id)
    if position:
        try:
            # Attempt to delete the Position
            session.delete(position)
            session.commit()
            log.info(f"🗑️ Deleted Position ID {position_id}")
        except Exception as e:
            session.rollback()
            log.error(f"⚠️ Cannot delete Position ID {position_id}: {e}")
            return False    
        return True
    else:
        log.warning(f"⚠️ Position ID {position_id} not found.")
        return False