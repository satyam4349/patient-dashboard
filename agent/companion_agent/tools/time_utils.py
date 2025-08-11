from datetime import datetime


def current_datetime_string() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


