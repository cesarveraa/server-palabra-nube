import random
from typing import Tuple, Optional

from google.cloud import firestore
from google.cloud.firestore_v1 import Increment

from app.config import settings
from app.utils.normalization import normalize_phrase
from app.utils.moderation import is_allowed
from app.utils.security import hmac_hash_ip_fp
from app.utils.timeutil import now_local, bucket_date_str
from app.services.rate_limit import rate_limit_minute_bucket


def should_bypass_daily(secret_from_header: Optional[str]) -> bool:
    return settings.BYPASS_DAILY or (settings.BYPASS_SECRET and secret_from_header == settings.BYPASS_SECRET)


def submit_phrase(
    db: firestore.Client,
    raw_text: str,
    ip: str,
    fp: Optional[str],
    secret_from_header: Optional[str] = None,  # nuevo parámetro
) -> Tuple[str, bool]:
    # 1) Normalización y moderación
    lemma = normalize_phrase(raw_text)
    if not is_allowed(lemma):
        raise ValueError("blocked")

    # 2) Rate limit por minuto (usa el helper ya parchado)
    _now = now_local()
    rate_limit_minute_bucket(db, hmac_hash_ip_fp(ip, fp or ""), _now)

    # 3) 1 por día (solo si no se debe omitir)
    if not should_bypass_daily(secret_from_header):
        day = bucket_date_str(_now)
        ip_hash = hmac_hash_ip_fp(ip, fp or "")
        daily_key = f"{ip_hash}:{day}"
        daily_ref = db.collection("daily_submissions").document(daily_key)

        @firestore.transactional
        def _create_daily_tx(transaction: firestore.Transaction):
            # ⬇️ usa ref.get(transaction=transaction)
            snap = daily_ref.get(transaction=transaction)
            if snap.exists:
                raise PermissionError("already_submitted_today")
            transaction.set(
                daily_ref,
                {"ipHash": ip_hash, "lemma": lemma, "ts": firestore.SERVER_TIMESTAMP},
                merge=False,
            )

        tx1 = db.transaction()
        _create_daily_tx(tx1)

    # 4) Incremento shardeado + materialización
    shard_id = random.randint(0, settings.SHARDS - 1)
    shard_ref = (
        db.collection("words")
        .document(lemma)
        .collection("shards")
        .document(str(shard_id))
    )
    word_ref = db.collection("words").document(lemma)

    @firestore.transactional
    def _inc_shard_and_total_tx(transaction: firestore.Transaction):
        # 1) LECTURAS PRIMERO
        shards_col = db.collection("words").document(lemma).collection("shards")
        total_old = 0
        for i in range(settings.SHARDS):
            sref = shards_col.document(str(i))
            ssnap = sref.get(transaction=transaction)
            total_old += int(ssnap.get("count") or 0)

        # 2) ESCRITURAS DESPUÉS
        # incrementa el shard elegido
        transaction.set(shard_ref, {"count": Increment(1)}, merge=True)

        # actualiza total (old + 1) y meta/version
        transaction.set(
            word_ref,
            {"total": total_old + 1, "updatedAt": firestore.SERVER_TIMESTAMP},
            merge=True,
        )
        meta_ref = db.collection("meta").document("state")
        transaction.set(
            meta_ref,
            {"version": Increment(1), "updatedAt": firestore.SERVER_TIMESTAMP},
            merge=True,
        )

    tx2 = db.transaction()
    _inc_shard_and_total_tx(tx2)

    return lemma, True


def fetch_wordcloud(db: firestore.Client, limit: int = 200):
    meta_ref = db.collection("meta").document("state")
    meta = meta_ref.get()
    version = int(meta.get("version") or 0) if meta.exists else 0

    updated_at_val = meta.get("updatedAt") if meta.exists else None
    updated_at = updated_at_val.isoformat() if updated_at_val else None

    docs = (
        db.collection("words")
        .order_by("total", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    items = [{"text": d.id, "count": int(d.get("total") or 0)} for d in docs]
    return {"version": version, "updatedAt": updated_at, "items": items}
