def write_to_db(amount: float) -> int:
    """Convert float amount to integer for DB storage (multiplied by 1,000,000)."""
    return int(round(amount * 1000000))

def read_from_db(cents: int) -> float:
    """Convert integer from DB to float amount (divided by 1,000,000)."""
    return cents / 1000000
