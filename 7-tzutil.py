"""Timezone step: birth place (lat, lon) + local civil date/time -> UTC offset hours (historical rules via IANA tz database)."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
def tz_name(lat, lon):
    from timezonefinder import TimezoneFinder
    n = TimezoneFinder().timezone_at(lat=lat, lng=lon)
    if not n: raise ValueError("no timezone for coordinates; pass tz name explicitly")
    return n
def offset_hours(local_dt, name, fold=0):
    """UTC offset in hours for naive local_dt in zone `name`. fold=0 picks the first of an ambiguous (DST-end) time. Raises for non-existent (DST-gap) times."""
    z = ZoneInfo(name)
    a = local_dt.replace(tzinfo=z, fold=fold)
    rt = a.astimezone(ZoneInfo("UTC")).astimezone(z).replace(tzinfo=None)
    if rt != local_dt:
        raise ValueError(f"{local_dt} does not exist in {name} (DST gap); ask the user for the correct time")
    return a.utcoffset().total_seconds() / 3600
def ambiguous(local_dt, name):
    z = ZoneInfo(name)
    return local_dt.replace(tzinfo=z, fold=0).utcoffset() != local_dt.replace(tzinfo=z, fold=1).utcoffset()
