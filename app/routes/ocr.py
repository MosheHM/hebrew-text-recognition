from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import Optional

from .. import schemas
from ..db import get_db
from ..services import user_project_service, file_handler

router = APIRouter(
    prefix="/ocr",
    tags=["ocr"],
)

@router.post("/upload-image/")
async def upload_image_and_create_project(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    project_name: str = Form(...),
    project_description: Optional[str] = Form(None),
    is_public: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Uploads an image, saves it, and creates a new project linked to the user.
    """
    # 1. Save the uploaded image
    try:
        saved_image_path = file_handler.save_uploaded_image(file)
    except HTTPException as e:
        raise e # Re-raise the HTTPException from file_handler
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save image: {e}"
        )

    # 2. Create a new project entry in the database
    try:
        # Check if user exists
        db_user = user_project_service.get_user(db, user_id=user_id)
        if db_user is None:
            # Clean up the saved image if user not found
            if saved_image_path.exists():
                saved_image_path.unlink()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        project_create_schema = schemas.ProjectCreate(
            name=project_name,
            description=project_description,
            image_path=str(saved_image_path), # Store the path
            is_public=is_public
        )
        db_project = user_project_service.create_project(db=db, project=project_create_schema, user_id=user_id)

        return {
            "message": "Image uploaded and project created successfully",
            "project_id": db_project.id,
            "image_path": str(saved_image_path)
        }

    except Exception as e:
        # Clean up the saved image if project creation fails
        if saved_image_path.exists():
            saved_image_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {e}"
        )