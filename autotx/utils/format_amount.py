from decimal import Decimal


def format_amount(amount: float) -> str:
    return format(Decimal(str(amount)), "f")