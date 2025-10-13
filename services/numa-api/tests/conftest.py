"""Global pytest configuration and shared fixtures for all tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="function")
def test_db_session():
    """Create a test database session using SQLite in-memory.

    This fixture creates a fresh database for each test function,
    ensuring tests are isolated and don't interfere with each other.
    """
    # Create in-memory SQLite database
    test_engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session factory
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Create session
    session = TestSessionLocal()
    
    # Override the get_db dependency with the test session
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db

    try:
        yield session
    finally:
        session.close()
        # Clean up the override
        app.dependency_overrides.clear()
