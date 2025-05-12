import pytest
from datetime import datetime
from typing import Optional

from app.schemas import (
    UserBase,
    UserCreate,
    User,
    ProjectBase,
    ProjectCreate,
    Project,
    UserProjectPermissionBase,
    UserProjectPermissionCreate,
    UserProjectPermission,
)

def test_user_base_schema():
    user_data = {"username": "testuser", "email": "test@example.com"}
    user = UserBase(**user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"

    user_data_no_email = {"username": "anotheruser"}
    user_no_email = UserBase(**user_data_no_email)
    assert user_no_email.username == "anotheruser"
    assert user_no_email.email is None

def test_user_create_schema():
    user_data = {"username": "newuser", "email": "new@example.com"}
    user = UserCreate(**user_data)
    assert user.username == "newuser"
    assert user.email == "new@example.com"

def test_user_schema():
    now = datetime.now()
    user_data = {
        "id": 1,
        "username": "existinguser",
        "email": "existing@example.com",
        "created_at": now,
        "updated_at": now,
    }
    user = User(**user_data)
    assert user.id == 1
    assert user.username == "existinguser"
    assert user.email == "existing@example.com"
    assert user.created_at == now
    assert user.updated_at == now

def test_project_base_schema():
    project_data = {"name": "Test Project", "description": "A project for testing", "is_public": True}
    project = ProjectBase(**project_data)
    assert project.name == "Test Project"
    assert project.description == "A project for testing"
    assert project.is_public is True

    project_data_defaults = {"name": "Another Project"}
    project_defaults = ProjectBase(**project_data_defaults)
    assert project_defaults.name == "Another Project"
    assert project_defaults.description is None
    assert project_defaults.is_public is False

def test_project_create_schema():
    project_data = {"name": "New Project", "description": "A new project"}
    project = ProjectCreate(**project_data)
    assert project.name == "New Project"
    assert project.description == "A new project"
    assert project.is_public is False # Default value

def test_project_schema():
    now = datetime.now()
    project_data = {
        "id": 1,
        "name": "Existing Project",
        "description": "An existing project",
        "is_public": False,
        "created_at": now,
        "updated_at": now,
        "permission_level": "admin",
    }
    project = Project(**project_data)
    assert project.id == 1
    assert project.name == "Existing Project"
    assert project.description == "An existing project"
    assert project.is_public is False
    assert project.created_at == now
    assert project.updated_at == now
    assert project.permission_level == "admin"

    project_data_no_permission = {
        "id": 2,
        "name": "Another Existing Project",
        "description": "Another existing project",
        "is_public": True,
        "created_at": now,
        "updated_at": now,
    }
    project_no_permission = Project(**project_data_no_permission)
    assert project_no_permission.id == 2
    assert project_no_permission.name == "Another Existing Project"
    assert project_no_permission.description == "Another existing project"
    assert project_no_permission.is_public is True
    assert project_no_permission.created_at == now
    assert project_no_permission.updated_at == now
    assert project_no_permission.permission_level is None

def test_user_project_permission_base_schema():
    permission_data = {"user_id": 1, "project_id": 1, "permission_level": "editor"}
    permission = UserProjectPermissionBase(**permission_data)
    assert permission.user_id == 1
    assert permission.project_id == 1
    assert permission.permission_level == "editor"

def test_user_project_permission_create_schema():
    permission_data = {"user_id": 1, "project_id": 1, "permission_level": "admin"}
    permission = UserProjectPermissionCreate(**permission_data)
    assert permission.user_id == 1
    assert permission.project_id == 1
    assert permission.permission_level == "admin"

def test_user_project_permission_schema():
    now = datetime.now()
    permission_data = {
        "user_id": 1,
        "project_id": 1,
        "permission_level": "viewer",
        "created_at": now,
        "updated_at": now,
    }
    permission = UserProjectPermission(**permission_data)
    assert permission.user_id == 1
    assert permission.project_id == 1
    assert permission.permission_level == "viewer"
    assert permission.created_at == now
    assert permission.updated_at == now