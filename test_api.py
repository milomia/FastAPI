from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from main import app, Base, get_db

# Setup the TestClient
client = TestClient(app)

# Setup the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///cakes.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


def test_create_item():
    response = client.post(
        "/cakes/", json={"name": "Test Cake", "comment": "This is a test cake", "imageUrl": "https://www.google.com", "yumFactor": 5}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Test Cake"
    assert data["comment"] == "This is a test cake"
    assert "id" in data


def test_read_item():
    # Create an item
    response = client.post(
        "/cakes/", json={"name": "Test Cake", "comment": "This is a test cake", "imageUrl": "https://www.google.com", "yumFactor": 5}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    cake_id = data["id"]
    
    response = client.get(f"/cakes/{cake_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Test Cake"
    assert data["comment"] == "This is a test cake"
    assert data["id"] == cake_id


def test_delete_item():
    cake_id = 1
    response = client.delete(f"/cakes/{cake_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == cake_id
    # Try to get the deleted item
    response = client.get(f"/cakes/{cake_id}")
    assert response.status_code == 404, response.text


def setup() -> None:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)


def teardown() -> None:
    # Drop the tables in the test database
    Base.metadata.drop_all(bind=engine)
