from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import or_

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate, user_id: int):
    db_project = models.Project(name=project.name, description=project.description, is_public=project.is_public)
    db.add(db_project)
    db.flush() # Use flush to get the new_project.id before commit

    # Add the creating user as admin
    db_permission = models.UserProjectPermission(user_id=user_id, project_id=db_project.id, permission_level='admin')
    db.add(db_permission)

    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, project_update: schemas.ProjectBase):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        for key, value in project_update.model_dump(exclude_unset=True).items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        # Delete associated permissions first
        db.query(models.UserProjectPermission).filter(models.UserProjectPermission.project_id == project_id).delete()
        db.delete(db_project)
        db.commit()
    return db_project

def get_user_projects(db: Session, user_id: int):
    # Query 1: Get projects where the user has explicit permissions
    user_project_ids = db.query(models.UserProjectPermission.project_id).filter(
        models.UserProjectPermission.user_id == user_id
    ).all()
    user_project_ids = [id[0] for id in user_project_ids]  # Extract project IDs from tuples
    
    # Query 2: Get public projects that the user doesn't already have permissions for
    public_projects = db.query(models.Project).filter(
        models.Project.is_public == True,
        ~models.Project.id.in_(user_project_ids) if user_project_ids else True
    ).all()
    
    # Query 3: Get projects where the user has explicit permissions
    permission_projects = db.query(models.Project).filter(
        models.Project.id.in_(user_project_ids)
    ).all() if user_project_ids else []
    
    # Combine the results
    projects = permission_projects + public_projects
    
    # For projects where the user has explicit permission, get the permission level
    user_permissions = db.query(models.UserProjectPermission).filter(
        models.UserProjectPermission.user_id == user_id
    ).all()
    permission_dict = {perm.project_id: perm.permission_level for perm in user_permissions}

    # Attach permission level to projects
    project_list = []
    for project in projects:
        # Create a dictionary manually to avoid validation errors with null fields
        project_data = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "image_path": project.image_path,
            "is_public": project.is_public,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "permission_level": permission_dict.get(project.id, 'public_access')  # Indicate public access if no specific permission
        }
        project_list.append(project_data)

    return project_list


def get_user_project_permission(db: Session, user_id: int, project_id: int):
    return db.query(models.UserProjectPermission).filter(
        models.UserProjectPermission.user_id == user_id,
        models.UserProjectPermission.project_id == project_id
    ).first()

def create_user_project_permission(db: Session, permission: schemas.UserProjectPermissionCreate):
    db_permission = models.UserProjectPermission(
        user_id=permission.user_id,
        project_id=permission.project_id,
        permission_level=permission.permission_level
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def update_user_project_permission(db: Session, user_id: int, project_id: int, permission_level: str):
    db_permission = db.query(models.UserProjectPermission).filter(
        models.UserProjectPermission.user_id == user_id,
        models.UserProjectPermission.project_id == project_id
    ).first()
    if db_permission:
        db_permission.permission_level = permission_level
        db.commit()
        db.refresh(db_permission)
    return db_permission

def delete_user_project_permission(db: Session, user_id: int, project_id: int):
    db_permission = db.query(models.UserProjectPermission).filter(
        models.UserProjectPermission.user_id == user_id,
        models.UserProjectPermission.project_id == project_id
    ).first()
    if db_permission:
        db.delete(db_permission)
        db.commit()
    return db_permission