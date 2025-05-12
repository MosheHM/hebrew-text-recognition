from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas
from ..db import get_db
from ..services import user_project_service

router = APIRouter(
    prefix="/api",
    tags=["users", "projects", "permissions"],
)

# User Endpoints

@router.post("/users/", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_project_service.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user_project_service.create_user(db=db, user=user)

@router.get("/users/", response_model=List[schemas.User])
def read_users_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # In a real application, this endpoint would require authentication/authorization
    users = user_project_service.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = user_project_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/users/{user_id}/projects/", response_model=List[schemas.Project])
def read_user_projects_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = user_project_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    projects = user_project_service.get_user_projects(db, user_id=user_id)
    return projects

# Project Endpoints

@router.post("/projects/", response_model=schemas.Project)
def create_project_endpoint(project: schemas.ProjectCreate, user_id: int, db: Session = Depends(get_db)):
    # In a real app, you'd get the creating user's ID from the authenticated session
    # For this basic implementation, user_id is provided as a query parameter
    db_user = user_project_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Creating user not found")

    return user_project_service.create_project(db=db, project=project, user_id=user_id)

@router.get("/projects/{project_id}", response_model=schemas.Project)
def read_project_endpoint(project_id: int, user_id: int = None, db: Session = Depends(get_db)):
    # In a real app, you'd check the authenticated user's permissions
    # For this basic implementation, we'll allow access if public or if a user_id is provided for check
    db_project = user_project_service.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if db_project.is_public:
        return db_project
    elif user_id:
        permission = user_project_service.get_user_project_permission(db, user_id=user_id, project_id=project_id)
        if permission:
            return db_project
        else:
            raise HTTPException(status_code=403, detail="User does not have permission to view this project")
    else:
        raise HTTPException(status_code=403, detail="Project is private, user_id required for access check")


@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project_endpoint(project_id: int, project_update: schemas.ProjectBase, user_id: int, db: Session = Depends(get_db)):
    # In a real app, you'd check the authenticated user's permissions ('admin' or 'model_editor')
    # For this basic implementation, user_id is provided as a query parameter for permission check
    permission = user_project_service.get_user_project_permission(db, user_id=user_id, project_id=project_id)
    if not permission or permission.permission_level not in ['admin', 'model_editor']:
        raise HTTPException(status_code=403, detail="User does not have sufficient permissions to update this project")

    db_project = user_project_service.update_project(db, project_id=project_id, project_update=project_update)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.delete("/projects/{project_id}", status_code=status.HTTP_200_OK)
def delete_project_endpoint(project_id: int, user_id: int, db: Session = Depends(get_db)):
    # In a real app, you'd check the authenticated user's permissions ('admin')
    # For this basic implementation, user_id is provided as a query parameter for permission check
    permission = user_project_service.get_user_project_permission(db, user_id=user_id, project_id=project_id)
    if not permission or permission.permission_level != 'admin':
        raise HTTPException(status_code=403, detail="User does not have sufficient permissions to delete this project")

    db_project = user_project_service.delete_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

# Project Permission Endpoints

@router.post("/projects/{project_id}/permissions/", response_model=schemas.UserProjectPermission)
def add_project_permission_endpoint(project_id: int, permission: schemas.UserProjectPermissionCreate, admin_user_id: int, db: Session = Depends(get_db)):
    # In a real app, you'd check the authenticated user's permissions ('admin' on the project)
    # For this basic implementation, admin_user_id is provided as a query parameter for permission check
    admin_permission = user_project_service.get_user_project_permission(db, user_id=admin_user_id, project_id=project_id)
    if not admin_permission or admin_permission.permission_level != 'admin':
        raise HTTPException(status_code=403, detail="User does not have admin permissions on this project")

    # Check if the project and user to add exist
    db_project = user_project_service.get_project(db, project_id=project_id)
    db_user_to_add = user_project_service.get_user(db, user_id=permission.user_id)

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not db_user_to_add:
        raise HTTPException(status_code=404, detail="User to add not found")

    # Check if permission already exists
    existing_permission = user_project_service.get_user_project_permission(db, user_id=permission.user_id, project_id=project_id)
    if existing_permission:
        raise HTTPException(status_code=409, detail="User already has permissions for this project")

    return user_project_service.create_user_project_permission(db=db, permission=permission)

@router.put("/projects/{project_id}/permissions/{user_id}", response_model=schemas.UserProjectPermission)
def update_project_permission_endpoint(project_id: int, user_id: int, permission_update: schemas.UserProjectPermissionBase, admin_user_id: int, db: Session = Depends(get_db)):
    # In a real app, you'd check the authenticated user's permissions ('admin' on the project)
    # For this basic implementation, admin_user_id is provided as a query parameter for permission check
    admin_permission = user_project_service.get_user_project_permission(db, user_id=admin_user_id, project_id=project_id)
    if not admin_permission or admin_permission.permission_level != 'admin':
        raise HTTPException(status_code=403, detail="User does not have admin permissions on this project")

    db_permission = user_project_service.update_user_project_permission(db, user_id=user_id, project_id=project_id, permission_level=permission_update.permission_level)
    if db_permission is None:
        raise HTTPException(status_code=404, detail="User permission not found for this project")
    return db_permission

@router.delete("/projects/{project_id}/permissions/{user_id}", status_code=status.HTTP_200_OK)
def remove_project_permission_endpoint(project_id: int, user_id: int, admin_user_id: int, db: Session = Depends(get_db)):
    # In a real app, you'd check the authenticated user's permissions ('admin' on the project)
    # For this basic implementation, admin_user_id is provided as a query parameter for permission check
    admin_permission = user_project_service.get_user_project_permission(db, user_id=admin_user_id, project_id=project_id)
    if not admin_permission or admin_permission.permission_level != 'admin':
        raise HTTPException(status_code=403, detail="User does not have admin permissions on this project")

    db_permission = user_project_service.delete_user_project_permission(db, user_id=user_id, project_id=project_id)
    if db_permission is None:
        raise HTTPException(status_code=404, detail="User permission not found for this project")
    return {"message": "User permission removed successfully"}