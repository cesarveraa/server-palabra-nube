from google.cloud import firestore
from google.oauth2 import service_account
from firebase_admin import initialize_app, credentials
from app.config import settings

_initialized = False
_db = None

def _service_account_info_from_env():
    # OJO: la private key viene con '\n' escapados en env; aquí los restauramos
    private_key = settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n")
    return {
        "type": "service_account",
        "project_id": settings.FIREBASE_PROJECT_ID,
        "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
        "private_key": private_key,
        "client_email": settings.FIREBASE_CLIENT_EMAIL,
        "client_id": settings.FIREBASE_CLIENT_ID,
        "auth_uri": settings.FIREBASE_AUTH_URI,
        "token_uri": settings.FIREBASE_TOKEN_URI,
        "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
        "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL or "",
    }

def get_db() -> firestore.Client:
    global _initialized, _db
    if not _initialized:
        sa_info = _service_account_info_from_env()
        gcp_creds = service_account.Credentials.from_service_account_info(sa_info)
        # Inicializa Firebase Admin con el dict (no archivo)
        try:
            initialize_app(credentials.Certificate(sa_info), {"projectId": settings.FIREBASE_PROJECT_ID})
        except ValueError:
            # ya estaba inicializado
            pass
        _db = firestore.Client(project=settings.FIREBASE_PROJECT_ID, credentials=gcp_creds)
        _initialized = True
    return _db
