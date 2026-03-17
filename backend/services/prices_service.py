from sqlalchemy.orm import Session
from repositories import prices_repository

class PriceDTO:
    def __init__(self, instrument_id: int, price: float, date):
        self.instrument_id = instrument_id
        self.price = price
        self.date = date

def get_latest_prices_for_instrument_list(session: Session, inst_ids: list[int]) -> list[PriceDTO]:
    """
    Returns a list of PriceDTOs with the latest price for each instrument in the list.
    """
    rows = prices_repository.get_latest_prices_for_instrument_list(session, inst_ids)
    
    # Rows are typically (instrument_id, price, date) tuples/objects
    # We need to convert price from DB integer to float if repository doesn't do it
    # repository returns: (instrument_id, price_int, date)
    
    from utils import read_from_db
    
    results = []
    for row in rows:
        # Check how row is returned (tuple or object?)
        # repository uses session.execute(stmt).all() which returns Row objects
        # Row objects can be accessed by index or attribute if labelled
        
        # In repo: select(Price.instrument_id, Price.price, subquery.c.latest_date.label("date"))
        
        inst_id = row.instrument_id
        price_int = row.price
        date = row.date
        
        results.append(PriceDTO(inst_id, read_from_db(price_int), date))
        
    return results
