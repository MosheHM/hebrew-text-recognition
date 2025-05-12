from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_path: Optional[str] = None # Add field for image path
    is_public: bool = False

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    image_path: Optional[str] = None # Add field for image path
    created_at: datetime
    updated_at: datetime
    permission_level: Optional[str] = None # To include permission level when listing user projects

    model_config = ConfigDict(from_attributes=True)

class UserProjectPermissionBase(BaseModel):
    user_id: int
    project_id: int
    permission_level: str

class UserProjectPermissionCreate(UserProjectPermissionBase):
    pass

class UserProjectPermission(UserProjectPermissionBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)