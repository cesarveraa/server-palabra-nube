import pytz
from datetime import datetime
from app.config import settings

def now_local():
    tz = pytz.timezone(settings.TIMEZONE)
    return datetime.now(tz)

def bucket_date_str(dt: datetime) -> str:
    return dt.strftime("%Y%m%d")
