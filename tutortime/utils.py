from datetime import datetime

DT_FORMAT = "%Y-%m-%dT%H:%M"


def dt_to_str(timestamp: datetime) -> str:
    return datetime.strftime(timestamp, DT_FORMAT)


def str_to_dt(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, DT_FORMAT)
