import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from datetime import datetime

from app.main import app
from app import schemas
from app.db import get_db
from app.services import user_project_service

# Use the TestClient for making requests to the FastAPI application
client = TestClient(app)

# Fixture to override the get_db dependency with a mock session
@pytest.fixture(scope="function")
def mock_db_session():
    session = MagicMock(spec=Session)
    yield session

# Fixture to override the get_db dependency in the app
@pytest.fixture(scope="function")
def override_get_db(mock_db_session):
    def _override_get_db():
        yield mock_db_session
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear() # Clear overrides after the test

# User Endpoint Tests

def test_create_user_endpoint(override_get_db, mock_db_session):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com")
    mock_db_session.query.return_value.filter.return_value.first.return_value = None # User does not exist
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None

    # Mock the service function call
    mock_created_user = schemas.User(id=1, username="testuser", email="test@example.com", created_at=datetime.now(), updated_at=datetime.now())
    user_project_service.create_user = MagicMock(return_value=mock_created_user)

    response = client.post("/api/users/", json=user_data.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_create_user_endpoint_username_exists(override_get_db, mock_db_session):
    user_data = schemas.UserCreate(username="existinguser", email="existing@example.com")
    mock_db_session.query.return_value.filter.return_value.first.return_value = schemas.User(id=1, username="existinguser", email="existing@example.com", created_at=datetime.now(), updated_at=datetime.now()) # User already exists

    response = client.post("/api/users/", json=user_data.model_dump())

    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}

def test_read_users_endpoint(override_get_db, mock_db_session):
    mock_users = [
        schemas.User(id=1, username="user1", email="user1@example.com", created_at=datetime.now(), updated_at=datetime.now()),
        schemas.User(id=2, username="user2", email="user2@example.com", created_at=datetime.now(), updated_at=datetime.now()),
    ]
    mock_db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_users

    # Mock the service function call
    user_project_service.get_users = MagicMock(return_value=mock_users)

    response = client.get("/api/users/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "user1"
    assert data[1]["username"] == "user2"

def test_read_user_endpoint(override_get_db, mock_db_session):
    mock_user = schemas.User(id=1, username="testuser", email="test@example.com", created_at=datetime.now(), updated_at=datetime.now())
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Mock the service function call
    user_project_service.get_user = MagicMock(return_value=mock_user)

    response = client.get("/api/users/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "testuser"

def test_read_user_endpoint_not_found(override_get_db, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    # Mock the service function call
    user_project_service.get_user = MagicMock(return_value=None)

    response = client.get("/api/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_read_user_projects_endpoint(override_get_db, mock_db_session):
    # Create a mock user
    mock_user = schemas.User(id=1, username="testuser", email="test@example.com", created_at=datetime.now(), updated_at=datetime.now())
    
    # Mock the user_project_service.get_user to return our mock user
    user_project_service.get_user = MagicMock(return_value=mock_user)

    # Create mock projects
    mock_projects = [
        {"id": 1, "name": "Project 1", "description": None, "is_public": False, "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat(), "permission_level": "admin"},
        {"id": 2, "name": "Public Project", "description": None, "is_public": True, "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat(), "permission_level": "public_access"},
    ]

    # Mock the service function call
    user_project_service.get_user_projects = MagicMock(return_value=mock_projects)

    # Make the request
    response = client.get("/api/users/1/projects/")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Project 1"
    assert data[0]["permission_level"] == "admin"
    assert data[1]["name"] == "Public Project"
    assert data[1]["permission_level"] == "public_access"

def test_read_user_projects_endpoint_user_not_found(override_get_db, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None # User does not exist

    # Mock the service function call
    user_project_service.get_user = MagicMock(return_value=None)

    response = client.get("/api/users/999/projects/")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

# Project Endpoint Tests

def test_create_project_endpoint(override_get_db, mock_db_session):
    user_id = 1
    project_data = schemas.ProjectCreate(name="New Project", description="A new project")

    mock_user = schemas.User(id=user_id, username="testuser", email="test@example.com", created_at=datetime.now(), updated_at=datetime.now())
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user # User exists

    mock_created_project = schemas.Project(id=1, name="New Project", description="A new project", is_public=False, created_at=datetime.now(), updated_at=datetime.now(), permission_level="admin")

    # Mock the service function call
    user_project_service.get_user = MagicMock(return_value=mock_user)
    user_project_service.create_project = MagicMock(return_value=mock_created_project)

    response = client.post(f"/api/projects/?user_id={user_id}", json=project_data.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Project"
    assert data["description"] == "A new project"
    assert data["is_public"] is False
    assert "id" in data

def test_create_project_endpoint_user_not_found(override_get_db, mock_db_session):
    user_id = 999
    project_data = schemas.ProjectCreate(name="New Project")

    mock_db_session.query.return_value.filter.return_value.first.return_value = None # User does not exist

    # Mock the service function call
    user_project_service.get_user = MagicMock(return_value=None)

    response = client.post(f"/api/projects/?user_id={user_id}", json=project_data.model_dump())

    assert response.status_code == 404
    assert response.json() == {"detail": "Creating user not found"}

def test_read_project_endpoint_public(override_get_db, mock_db_session):
    project_id = 1
    mock_project = schemas.Project(id=project_id, name="Public Project", description="This is public", is_public=True, created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function call
    user_project_service.get_project = MagicMock(return_value=mock_project)

    response = client.get(f"/api/projects/{project_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Public Project"
    assert data["is_public"] is True

def test_read_project_endpoint_private_with_permission(override_get_db, mock_db_session):
    project_id = 1
    user_id = 1
    mock_project = schemas.Project(id=project_id, name="Private Project", description="This is private", is_public=False, created_at=datetime.now(), updated_at=datetime.now())
    mock_permission = schemas.UserProjectPermission(user_id=user_id, project_id=project_id, permission_level="viewer", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_project = MagicMock(return_value=mock_project)
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_permission)

    response = client.get(f"/api/projects/{project_id}?user_id={user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Private Project"
    assert data["is_public"] is False

def test_read_project_endpoint_private_no_permission(override_get_db, mock_db_session):
    project_id = 1
    user_id = 1
    mock_project = schemas.Project(id=project_id, name="Private Project", description="This is private", is_public=False, created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_project = MagicMock(return_value=mock_project)
    user_project_service.get_user_project_permission = MagicMock(return_value=None) # No permission

    response = client.get(f"/api/projects/{project_id}?user_id={user_id}")

    assert response.status_code == 403
    assert response.json() == {"detail": "User does not have permission to view this project"}

def test_read_project_endpoint_private_no_user_id(override_get_db, mock_db_session):
    project_id = 1
    mock_project = schemas.Project(id=project_id, name="Private Project", description="This is private", is_public=False, created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function call
    user_project_service.get_project = MagicMock(return_value=mock_project)

    response = client.get(f"/api/projects/{project_id}")

    assert response.status_code == 403
    assert response.json() == {"detail": "Project is private, user_id required for access check"}

def test_read_project_endpoint_not_found(override_get_db, mock_db_session):
    project_id = 999

    # Mock the service function call
    user_project_service.get_project = MagicMock(return_value=None)

    response = client.get(f"/api/projects/{project_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

def test_update_project_endpoint(override_get_db, mock_db_session):
    project_id = 1
    user_id = 1
    project_update_data = schemas.ProjectBase(name="Updated Name", description="Updated Description", is_public=True)

    mock_permission = schemas.UserProjectPermission(user_id=user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())
    mock_updated_project = schemas.Project(id=project_id, name="Updated Name", description="Updated Description", is_public=True, created_at=datetime.now(), updated_at=datetime.now(), permission_level="admin")

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_permission)
    user_project_service.update_project = MagicMock(return_value=mock_updated_project)

    response = client.put(f"/api/projects/{project_id}?user_id={user_id}", json=project_update_data.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated Description"
    assert data["is_public"] is True

def test_update_project_endpoint_insufficient_permissions(override_get_db, mock_db_session):
    project_id = 1
    user_id = 1
    project_update_data = schemas.ProjectBase(name="Updated Name")

    mock_permission = schemas.UserProjectPermission(user_id=user_id, project_id=project_id, permission_level="viewer", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function call
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_permission)

    response = client.put(f"/api/projects/{project_id}?user_id={user_id}", json=project_update_data.model_dump())

    assert response.status_code == 403
    assert response.json() == {"detail": "User does not have sufficient permissions to update this project"}

def test_update_project_endpoint_project_not_found(override_get_db, mock_db_session):
    project_id = 999
    user_id = 1
    project_update_data = schemas.ProjectBase(name="Updated Name")

    mock_permission = schemas.UserProjectPermission(user_id=user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_permission)
    user_project_service.update_project = MagicMock(return_value=None) # Project not found by service

    response = client.put(f"/api/projects/{project_id}?user_id={user_id}", json=project_update_data.model_dump())

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

def test_delete_project_endpoint(override_get_db, mock_db_session):
    project_id = 1
    user_id = 1

    mock_permission = schemas.UserProjectPermission(user_id=user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())
    mock_deleted_project = schemas.Project(id=project_id, name="Deleted Project", description="", is_public=False, created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_permission)
    user_project_service.delete_project = MagicMock(return_value=mock_deleted_project)

    response = client.delete(f"/api/projects/{project_id}?user_id={user_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Project deleted successfully"}

def test_delete_project_endpoint_insufficient_permissions(override_get_db, mock_db_session):
    project_id = 1
    user_id = 1

    mock_permission = schemas.UserProjectPermission(user_id=user_id, project_id=project_id, permission_level="editor", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function call
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_permission)

    response = client.delete(f"/api/projects/{project_id}?user_id={user_id}")

    assert response.status_code == 403
    assert response.json() == {"detail": "User does not have sufficient permissions to delete this project"}

def test_delete_project_endpoint_project_not_found(override_get_db, mock_db_session):
    project_id = 999
    user_id = 1

    mock_permission = schemas.UserProjectPermission(user_id=user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_permission)
    user_project_service.delete_project = MagicMock(return_value=None) # Project not found by service

    response = client.delete(f"/api/projects/{project_id}?user_id={user_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

# Project Permission Endpoints

def test_add_project_permission_endpoint(override_get_db, mock_db_session):
    project_id = 1
    admin_user_id = 1
    user_to_add_id = 2
    permission_data = schemas.UserProjectPermissionCreate(user_id=user_to_add_id, project_id=project_id, permission_level="editor")

    mock_admin_permission = schemas.UserProjectPermission(user_id=admin_user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())
    mock_project = schemas.Project(id=project_id, name="Test Project", is_public=False, created_at=datetime.now(), updated_at=datetime.now())
    mock_user_to_add = schemas.User(id=user_to_add_id, username="user_to_add", created_at=datetime.now(), updated_at=datetime.now())
    mock_created_permission = schemas.UserProjectPermission(user_id=user_to_add_id, project_id=project_id, permission_level="editor", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(side_effect=[mock_admin_permission, None]) # First call for admin, second for existing permission
    user_project_service.get_project = MagicMock(return_value=mock_project)
    user_project_service.get_user = MagicMock(return_value=mock_user_to_add)
    user_project_service.create_user_project_permission = MagicMock(return_value=mock_created_permission)

    response = client.post(f"/api/projects/{project_id}/permissions/?admin_user_id={admin_user_id}", json=permission_data.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_to_add_id
    assert data["project_id"] == project_id
    assert data["permission_level"] == "editor"

def test_add_project_permission_endpoint_not_admin(override_get_db, mock_db_session):
    project_id = 1
    admin_user_id = 1 # This user is not an admin
    user_to_add_id = 2
    permission_data = schemas.UserProjectPermissionCreate(user_id=user_to_add_id, project_id=project_id, permission_level="editor")

    mock_permission = schemas.UserProjectPermission(user_id=admin_user_id, project_id=project_id, permission_level="viewer", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function call
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_permission)

    response = client.post(f"/api/projects/{project_id}/permissions/?admin_user_id={admin_user_id}", json=permission_data.model_dump())

    assert response.status_code == 403
    assert response.json() == {"detail": "User does not have admin permissions on this project"}

def test_add_project_permission_endpoint_project_not_found(override_get_db, mock_db_session):
    project_id = 999
    admin_user_id = 1
    user_to_add_id = 2
    permission_data = schemas.UserProjectPermissionCreate(user_id=user_to_add_id, project_id=project_id, permission_level="editor")

    mock_admin_permission = schemas.UserProjectPermission(user_id=admin_user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_admin_permission)
    user_project_service.get_project = MagicMock(return_value=None) # Project not found

    response = client.post(f"/api/projects/{project_id}/permissions/?admin_user_id={admin_user_id}", json=permission_data.model_dump())

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

def test_add_project_permission_endpoint_user_to_add_not_found(override_get_db, mock_db_session):
    project_id = 1
    admin_user_id = 1
    user_to_add_id = 999
    permission_data = schemas.UserProjectPermissionCreate(user_id=user_to_add_id, project_id=project_id, permission_level="editor")

    mock_admin_permission = schemas.UserProjectPermission(user_id=admin_user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())
    mock_project = schemas.Project(id=project_id, name="Test Project", is_public=False, created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_admin_permission)
    user_project_service.get_project = MagicMock(return_value=mock_project)
    user_project_service.get_user = MagicMock(return_value=None) # User to add not found

    response = client.post(f"/api/projects/{project_id}/permissions/?admin_user_id={admin_user_id}", json=permission_data.model_dump())

    assert response.status_code == 404
    assert response.json() == {"detail": "User to add not found"}

def test_add_project_permission_endpoint_permission_exists(override_get_db, mock_db_session):
    project_id = 1
    admin_user_id = 1
    user_to_add_id = 2
    permission_data = schemas.UserProjectPermissionCreate(user_id=user_to_add_id, project_id=project_id, permission_level="editor")

    mock_admin_permission = schemas.UserProjectPermission(user_id=admin_user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())
    mock_project = schemas.Project(id=project_id, name="Test Project", is_public=False, created_at=datetime.now(), updated_at=datetime.now())
    mock_user_to_add = schemas.User(id=user_to_add_id, username="user_to_add", created_at=datetime.now(), updated_at=datetime.now())
    mock_existing_permission = schemas.UserProjectPermission(user_id=user_to_add_id, project_id=project_id, permission_level="viewer", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(side_effect=[mock_admin_permission, mock_existing_permission]) # First call for admin, second for existing permission
    user_project_service.get_project = MagicMock(return_value=mock_project)
    user_project_service.get_user = MagicMock(return_value=mock_user_to_add)

    response = client.post(f"/api/projects/{project_id}/permissions/?admin_user_id={admin_user_id}", json=permission_data.model_dump())

    assert response.status_code == 409
    assert response.json() == {"detail": "User already has permissions for this project"}

def test_update_project_permission_endpoint(override_get_db, mock_db_session):
    project_id = 1
    user_id = 2
    admin_user_id = 1
    permission_update_data = schemas.UserProjectPermissionBase(user_id=user_id, project_id=project_id, permission_level="admin")

    mock_admin_permission = schemas.UserProjectPermission(user_id=admin_user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())
    mock_updated_permission = schemas.UserProjectPermission(user_id=user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_admin_permission)
    user_project_service.update_user_project_permission = MagicMock(return_value=mock_updated_permission)

    response = client.put(f"/api/projects/{project_id}/permissions/{user_id}?admin_user_id={admin_user_id}", json=permission_update_data.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["project_id"] == project_id
    assert data["permission_level"] == "admin"

def test_update_project_permission_endpoint_not_admin(override_get_db, mock_db_session):
    project_id = 1
    user_id = 2
    admin_user_id = 1 # This user is not an admin
    permission_update_data = schemas.UserProjectPermissionBase(user_id=user_id, project_id=project_id, permission_level="admin")

    mock_permission = schemas.UserProjectPermission(user_id=admin_user_id, project_id=project_id, permission_level="viewer", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function call
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_permission)

    response = client.put(f"/api/projects/{project_id}/permissions/{user_id}?admin_user_id={admin_user_id}", json=permission_update_data.model_dump())

    assert response.status_code == 403
    assert response.json() == {"detail": "User does not have admin permissions on this project"}

def test_update_project_permission_endpoint_permission_not_found(override_get_db, mock_db_session):
    project_id = 1
    user_id = 999 # Permission for this user does not exist
    admin_user_id = 1
    permission_update_data = schemas.UserProjectPermissionBase(user_id=user_id, project_id=project_id, permission_level="admin")

    mock_admin_permission = schemas.UserProjectPermission(user_id=admin_user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_admin_permission)
    user_project_service.update_user_project_permission = MagicMock(return_value=None) # Permission not found by service

    response = client.put(f"/api/projects/{project_id}/permissions/{user_id}?admin_user_id={admin_user_id}", json=permission_update_data.model_dump())

    assert response.status_code == 404
    assert response.json() == {"detail": "User permission not found for this project"}

def test_remove_project_permission_endpoint(override_get_db, mock_db_session):
    project_id = 1
    user_id = 2
    admin_user_id = 1

    mock_admin_permission = schemas.UserProjectPermission(user_id=admin_user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())
    mock_deleted_permission = schemas.UserProjectPermission(user_id=user_id, project_id=project_id, permission_level="editor", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_admin_permission)
    user_project_service.delete_user_project_permission = MagicMock(return_value=mock_deleted_permission)

    response = client.delete(f"/api/projects/{project_id}/permissions/{user_id}?admin_user_id={admin_user_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "User permission removed successfully"}

def test_remove_project_permission_endpoint_not_admin(override_get_db, mock_db_session):
    project_id = 1
    user_id = 2
    admin_user_id = 1 # This user is not an admin

    mock_permission = schemas.UserProjectPermission(user_id=admin_user_id, project_id=project_id, permission_level="editor", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function call
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_permission)

    response = client.delete(f"/api/projects/{project_id}/permissions/{user_id}?admin_user_id={admin_user_id}")

    assert response.status_code == 403
    assert response.json() == {"detail": "User does not have admin permissions on this project"}

def test_remove_project_permission_endpoint_permission_not_found(override_get_db, mock_db_session):
    project_id = 1
    user_id = 999 # Permission for this user does not exist
    admin_user_id = 1

    mock_admin_permission = schemas.UserProjectPermission(user_id=admin_user_id, project_id=project_id, permission_level="admin", created_at=datetime.now(), updated_at=datetime.now())

    # Mock the service function calls
    user_project_service.get_user_project_permission = MagicMock(return_value=mock_admin_permission)
    user_project_service.delete_user_project_permission = MagicMock(return_value=None) # Permission not found by service

    response = client.delete(f"/api/projects/{project_id}/permissions/{user_id}?admin_user_id={admin_user_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "User permission not found for this project"}