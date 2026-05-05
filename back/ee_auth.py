import json
import os
from pathlib import Path

import ee
from dotenv import load_dotenv


load_dotenv()

_ee_initialized = False


def _resolve_credentials_path(configured_path: str | None) -> Path | None:
    if not configured_path:
        return None

    original_path = Path(configured_path).expanduser()
    if original_path.exists():
        return original_path

    filename = original_path.name
    candidates = [
        Path("/back/credentials") / filename,
        Path(__file__).resolve().parent / "credentials" / filename,
        Path.cwd() / "credentials" / filename,
        Path.cwd() / "back" / "credentials" / filename,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return original_path


def _resolve_service_account(configured_account: str | None, credentials_path: Path | None) -> str | None:
    if configured_account:
        return configured_account

    if not credentials_path or not credentials_path.exists():
        return None

    with credentials_path.open(encoding="utf-8") as credentials_file:
        credentials = json.load(credentials_file)

    return credentials.get("client_email")


def initialize_ee() -> None:
    global _ee_initialized
    if _ee_initialized:
        return

    project = os.getenv("EE_PROJECT_NAME", "mseml-488016")
    credentials_path = _resolve_credentials_path(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    service_account = _resolve_service_account(os.getenv("EE_SERVICE_ACCOUNT"), credentials_path)

    if credentials_path is None:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS is not set")
    if not credentials_path.exists():
        raise RuntimeError(f"GEE credentials file not found: {credentials_path}")
    if not service_account:
        raise RuntimeError("EE_SERVICE_ACCOUNT is not set and could not be read from the credentials file")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
    credentials = ee.ServiceAccountCredentials(service_account, str(credentials_path))
    ee.Initialize(credentials=credentials, project=project)
    _ee_initialized = True
