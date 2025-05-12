from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from fastapi import FastAPI
from .db import Base, engine
from .routes import projects, ocr # Import the new ocr router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(projects.router)
app.include_router(ocr.router) # Include the new ocr router

# You would include other routers here as they are implemented
# app.include_router(feedback.router)