import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.main import app

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c 