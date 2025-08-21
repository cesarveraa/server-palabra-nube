from google.cloud import firestore
from datetime import datetime
from app.config import settings

def rate_limit_minute_bucket(db: firestore.Client, key: str, now: datetime) -> None:
    bucket = f"{now.year:04d}{now.month:02d}{now.day:02d}{now.hour:02d}{now.minute:02d}"
    doc_id = f"{key}:{bucket}"
    ref = db.collection("ratelimits").document(doc_id)

    @firestore.transactional
    def _tx(transaction: firestore.Transaction):
        # ⬇️ usa ref.get(transaction=transaction)
        snap = ref.get(transaction=transaction)
        count = snap.get("count") if snap.exists else 0
        if count >= settings.RATE_LIMIT_PER_MINUTE:
            raise PermissionError("rate_limit")
        # ⬇️ escribe con transaction.set(...)
        transaction.set(ref, {"count": count + 1, "ts": firestore.SERVER_TIMESTAMP}, merge=True)

    tx = db.transaction()
    _tx(tx)
