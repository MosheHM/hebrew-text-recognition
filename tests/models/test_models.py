import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base, User, Project, UserProjectPermission

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
    user = User(username="testuser", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.created_at is not None
    assert user.updated_at is None # updated_at should be None on creation

def test_create_project(db_session):
    project = Project(name="Test Project", description="A project for testing")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    assert project.id is not None
    assert project.name == "Test Project"
    assert project.description == "A project for testing"
    assert project.is_public is False
    assert project.created_at is not None
    assert project.updated_at is None

def test_create_user_project_permission(db_session):
    user = User(username="testuser", email="test@example.com")
    project = Project(name="Test Project", description="A project for testing")
    db_session.add(user)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(project)

    permission = UserProjectPermission(user_id=user.id, project_id=project.id, permission_level="admin")
    db_session.add(permission)
    db_session.commit()
    db_session.refresh(permission)

    assert permission.user_id == user.id
    assert permission.project_id == project.id
    assert permission.permission_level == "admin"
    assert permission.created_at is not None
    assert permission.updated_at is None

def test_user_project_relationship(db_session):
    user = User(username="testuser", email="test@example.com")
    project = Project(name="Test Project", description="A project for testing")
    db_session.add(user)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(project)

    permission = UserProjectPermission(user=user, project=project, permission_level="editor")
    db_session.add(permission)
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(project)
    db_session.refresh(permission)

    assert len(user.permissions) == 1
    assert user.permissions[0].permission_level == "editor"
    assert user.permissions[0].project.name == "Test Project"

    assert len(project.permissions) == 1
    assert project.permissions[0].permission_level == "editor"
    assert project.permissions[0].user.username == "testuser"