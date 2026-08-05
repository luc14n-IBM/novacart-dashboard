"""
conftest.py — Shared pytest fixtures for the NovaCart API test suite.

Two client fixtures are provided:
  - client      : Dev mode (CLIENT_VALIDATION=Dev, DATA_BACKEND=sqlite)
  - spcs_client : SPCS mode (CLIENT_VALIDATION=SPCS, DATA_BACKEND=sqlite)

Both point to the real novacart_gold.db SQLite file so queries run against
actual data without requiring any mocking or fixtures for database content.
"""

import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient


# Absolute path to the shared SQLite database
_DB_PATH = str(Path(__file__).parent.parent / "data" / "novacart_gold.db")

# Set env vars once before any import so module-level reads in main.py and
# connection.py pick up the correct values on first load.
os.environ["DATA_BACKEND"]      = "sqlite"
os.environ["SQLITE_PATH"]       = _DB_PATH
os.environ["CLIENT_VALIDATION"] = "Dev"

from main import app  # noqa: E402  (must come after env setup)
import main as _main_module  # noqa: E402


@pytest.fixture(scope="session")
def client():
    """
    FastAPI TestClient in Dev mode.
    CORS middleware is active; authorize returns mock user.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def spcs_client():
    """
    FastAPI TestClient that exercises the SPCS authorize path.
    Patches main.CLIENT_VALIDATION in-place so the already-imported module
    sees SPCS mode without a reload.
    """
    original = _main_module.CLIENT_VALIDATION
    _main_module.CLIENT_VALIDATION = "SPCS"
    try:
        with TestClient(app) as c:
            yield c
    finally:
        _main_module.CLIENT_VALIDATION = original
