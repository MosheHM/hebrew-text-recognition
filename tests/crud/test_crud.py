import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models, schemas
from app import crud
from app.db import Base # Assuming Base is defined in app.db

@pytest.fixture(scope="module")
def engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything"""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_create_user(db_session):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com")
    db_user = crud.create_user(db_session, user=user_data)

    assert db_user.id is not None
    assert db_user.username == "testuser"
    assert db_user.email == "test@example.com"

def test_get_user(db_session):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com")
    db_user = crud.create_user(db_session, user=user_data)

    fetched_user = crud.get_user(db_session, user_id=db_user.id)
    assert fetched_user is not None
    assert fetched_user.id == db_user.id
    assert fetched_user.username == "testuser"

def test_get_user_by_username(db_session):
    user_data = schemas.UserCreate(username="testuser", email="test@example.com")
    db_user = crud.create_user(db_session, user=user_data)

    fetched_user = crud.get_user_by_username(db_session, username="testuser")
    assert fetched_user is not None
    assert fetched_user.id == db_user.id
    assert fetched_user.username == "testuser"

def test_get_users(db_session):
    user_data1 = schemas.UserCreate(username="testuser1")
    crud.create_user(db_session, user=user_data1)
    user_data2 = schemas.UserCreate(username="testuser2")
    crud.create_user(db_session, user=user_data2)

    users = crud.get_users(db_session)
    assert len(users) == 2
    assert any(user.username == "testuser1" for user in users)
    assert any(user.username == "testuser2" for user in users)

def test_create_project(db_session):
    user_data = schemas.UserCreate(username="testuser")
    db_user = crud.create_user(db_session, user=user_data)

    project_data = schemas.ProjectCreate(name="Test Project", description="A project for testing")
    db_project = crud.create_project(db_session, project=project_data, user_id=db_user.id)

    assert db_project.id is not None
    assert db_project.name == "Test Project"
    assert db_project.description == "A project for testing"
    assert db_project.is_public is False

    # Verify admin permission is created
    permission = crud.get_user_project_permission(db_session, user_id=db_user.id, project_id=db_project.id)
    assert permission is not None
    assert permission.permission_level == "admin"

def test_get_project(db_session):
    user_data = schemas.UserCreate(username="testuser")
    db_user = crud.create_user(db_session, user=user_data)
    project_data = schemas.ProjectCreate(name="Test Project")
    db_project = crud.create_project(db_session, project=project_data, user_id=db_user.id)

    fetched_project = crud.get_project(db_session, project_id=db_project.id)
    assert fetched_project is not None
    assert fetched_project.id == db_project.id
    assert fetched_project.name == "Test Project"

def test_get_projects(db_session):
    user_data = schemas.UserCreate(username="testuser")
    db_user = crud.create_user(db_session, user=user_data)
    project_data1 = schemas.ProjectCreate(name="Test Project 1")
    crud.create_project(db_session, project=project_data1, user_id=db_user.id)
    project_data2 = schemas.ProjectCreate(name="Test Project 2")
    crud.create_project(db_session, project=project_data2, user_id=db_user.id)

    projects = crud.get_projects(db_session)
    assert len(projects) == 2
    assert any(project.name == "Test Project 1" for project in projects)
    assert any(project.name == "Test Project 2" for project in projects)

def test_update_project(db_session):
    user_data = schemas.UserCreate(username="testuser")
    db_user = crud.create_user(db_session, user=user_data)
    project_data = schemas.ProjectCreate(name="Test Project", description="Initial description")
    db_project = crud.create_project(db_session, project=project_data, user_id=db_user.id)

    update_data = schemas.ProjectBase(name="Updated Project", description="Updated description", is_public=True)
    updated_project = crud.update_project(db_session, project_id=db_project.id, project_update=update_data)

    assert updated_project is not None
    assert updated_project.id == db_project.id
    assert updated_project.name == "Updated Project"
    assert updated_project.description == "Updated description"
    assert updated_project.is_public is True

def test_delete_project(db_session):
    user_data = schemas.UserCreate(username="testuser")
    db_user = crud.create_user(db_session, user=user_data)
    project_data = schemas.ProjectCreate(name="Test Project")
    db_project = crud.create_project(db_session, project=project_data, user_id=db_user.id)

    # Verify project and permission exist before deletion
    initial_project = crud.get_project(db_session, project_id=db_project.id)
    initial_permission = crud.get_user_project_permission(db_session, user_id=db_user.id, project_id=db_project.id)
    assert initial_project is not None
    assert initial_permission is not None

    deleted_project = crud.delete_project(db_session, project_id=db_project.id)
    assert deleted_project is not None
    assert deleted_project.id == db_project.id

    # Verify project and permission are deleted
    fetched_project = crud.get_project(db_session, project_id=db_project.id)
    fetched_permission = crud.get_user_project_permission(db_session, user_id=db_user.id, project_id=db_project.id)
    assert fetched_project is None
    assert fetched_permission is None

def test_get_user_projects(db_session):
    user1_data = schemas.UserCreate(username="user1")
    user1 = crud.create_user(db_session, user=user1_data)
    user2_data = schemas.UserCreate(username="user2")
    user2 = crud.create_user(db_session, user=user2_data)

    project1_data = schemas.ProjectCreate(name="User1's Project", is_public=False)
    project1 = crud.create_project(db_session, project=project1_data, user_id=user1.id) # user1 is admin

    project2_data = schemas.ProjectCreate(name="Public Project", is_public=True)
    project2 = crud.create_project(db_session, project=project2_data, user_id=user1.id) # user1 is admin

    project3_data = schemas.ProjectCreate(name="User2's Project", is_public=False)
    project3 = crud.create_project(db_session, project=project3_data, user_id=user2.id) # user2 is admin

    # Give user2 permission to project1
    permission_data = schemas.UserProjectPermissionCreate(user_id=user2.id, project_id=project1.id, permission_level="viewer")
    crud.create_user_project_permission(db_session, permission=permission_data)

    # Get projects for user1
    user1_projects = crud.get_user_projects(db_session, user_id=user1.id)
    assert len(user1_projects) == 2
    assert any(p['name'] == "User1's Project" and p['permission_level'] == 'admin' for p in user1_projects)
    assert any(p['name'] == "Public Project" and p['permission_level'] == 'admin' for p in user1_projects) # User1 is admin of public project

    # Get projects for user2
    user2_projects = crud.get_user_projects(db_session, user_id=user2.id)
    assert len(user2_projects) == 3  # User2 should see 3 projects: their own project, the project they have permission for, and the public project
    assert any(p['name'] == "User1's Project" and p['permission_level'] == 'viewer' for p in user2_projects)
    assert any(p['name'] == "User2's Project" and p['permission_level'] == 'admin' for p in user2_projects)
    assert any(p['name'] == "Public Project" and p['permission_level'] == 'public_access' for p in user2_projects) # User2 has public access

def test_get_user_project_permission(db_session):
    user_data = schemas.UserCreate(username="testuser")
    db_user = crud.create_user(db_session, user=user_data)
    project_data = schemas.ProjectCreate(name="Test Project")
    db_project = crud.create_project(db_session, project=project_data, user_id=db_user.id) # Creates admin permission

    permission = crud.get_user_project_permission(db_session, user_id=db_user.id, project_id=db_project.id)
    assert permission is not None
    assert permission.user_id == db_user.id
    assert permission.project_id == db_project.id
    assert permission.permission_level == "admin"

    non_existent_permission = crud.get_user_project_permission(db_session, user_id=db_user.id, project_id=999)
    assert non_existent_permission is None

def test_create_user_project_permission(db_session):
    user_data = schemas.UserCreate(username="testuser")
    db_user = crud.create_user(db_session, user=user_data)
    project_data = schemas.ProjectCreate(name="Test Project")
    db_project = crud.create_project(db_session, project=project_data, user_id=db_user.id) # Creates admin permission

    permission_data = schemas.UserProjectPermissionCreate(user_id=db_user.id, project_id=db_project.id, permission_level="editor")
    # Attempting to create a permission that already exists (admin) will likely raise an integrity error depending on DB constraints,
    # but the crud function doesn't handle this. We'll test creating a new permission for a different user or project later if needed.
    # For now, let's test creating a permission for a different user on this project.
    user2_data = schemas.UserCreate(username="testuser2")
    db_user2 = crud.create_user(db_session, user=user2_data)
    permission_data_user2 = schemas.UserProjectPermissionCreate(user_id=db_user2.id, project_id=db_project.id, permission_level="viewer")
    db_permission = crud.create_user_project_permission(db_session, permission=permission_data_user2)

    assert db_permission.user_id == db_user2.id
    assert db_permission.project_id == db_project.id
    assert db_permission.permission_level == "viewer"

def test_update_user_project_permission(db_session):
    user_data = schemas.UserCreate(username="testuser")
    db_user = crud.create_user(db_session, user=user_data)
    project_data = schemas.ProjectCreate(name="Test Project")
    db_project = crud.create_project(db_session, project=project_data, user_id=db_user.id) # Creates admin permission

    updated_permission = crud.update_user_project_permission(db_session, user_id=db_user.id, project_id=db_project.id, permission_level="editor")
    assert updated_permission is not None
    assert updated_permission.user_id == db_user.id
    assert updated_permission.project_id == db_project.id
    assert updated_permission.permission_level == "editor"

    non_existent_permission = crud.update_user_project_permission(db_session, user_id=db_user.id, project_id=999, permission_level="viewer")
    assert non_existent_permission is None

def test_delete_user_project_permission(db_session):
    user_data = schemas.UserCreate(username="testuser")
    db_user = crud.create_user(db_session, user=user_data)
    project_data = schemas.ProjectCreate(name="Test Project")
    db_project = crud.create_project(db_session, project=project_data, user_id=db_user.id) # Creates admin permission

    # Verify permission exists before deletion
    initial_permission = crud.get_user_project_permission(db_session, user_id=db_user.id, project_id=db_project.id)
    assert initial_permission is not None

    deleted_permission = crud.delete_user_project_permission(db_session, user_id=db_user.id, project_id=db_project.id)
    assert deleted_permission is not None
    assert deleted_permission.user_id == db_user.id
    assert deleted_permission.project_id == db_project.id

    # Verify permission is deleted
    fetched_permission = crud.get_user_project_permission(db_session, user_id=db_user.id, project_id=db_project.id)
    assert fetched_permission is None

    non_existent_permission = crud.delete_user_project_permission(db_session, user_id=db_user.id, project_id=999)
    assert non_existent_permission is None