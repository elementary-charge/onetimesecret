import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

import settings
from app.main import app


@pytest.fixture(scope='session')
def _mongo_client() -> MongoClient:
    with MongoClient(settings.MONGO_URI) as client:
        yield client


@pytest.fixture
def _clear_db(_mongo_client: MongoClient):
    _mongo_client.drop_database(settings.MONGO_DATABASE)


@pytest.fixture
def web_client(_clear_db) -> TestClient:
    with TestClient(app) as client:
        yield client
