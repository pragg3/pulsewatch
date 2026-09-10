import os

# Test-only configuration.
# These values must be set before backend.app.main is imported.
os.environ["NETWORK_DISCOVERY_ENABLED"] = "true"
os.environ["NETWORK_DISCOVERY_KEY"] = "test-discovery-key"
os.environ["NETWORK_MAX_SCAN_HOSTS"] = "512"
os.environ["NETWORK_SCAN_CONCURRENCY"] = "32"
os.environ["NETWORK_PROBE_TIMEOUT_SECONDS"] = "0.8"

# Keep normal tests away from the production 5/minute limit.
# Rate limiting is verified separately.
os.environ["NETWORK_SCAN_RATE_LIMIT"] = "1000/minute"

os.environ["NETWORK_TRUST_PROXY_HEADERS"] = "false"


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base, get_db
from backend.app.main import app

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(
        app,
        headers={
            "X-PulseWatch-Discovery-Key": "test-discovery-key",
        },
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
