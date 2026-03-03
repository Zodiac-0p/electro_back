from pathlib import Path
import firebase_admin
from firebase_admin import credentials

def init_firebase():
    if firebase_admin._apps:
        return

    BASE_DIR = Path(__file__).resolve().parent.parent  # backend root
    cred_path = BASE_DIR / "secrets" / "firebase-service.json"

    if not cred_path.exists():
        raise FileNotFoundError(f"Firebase credentials file not found: {cred_path}")

    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)