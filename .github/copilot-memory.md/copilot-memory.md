# 🧠 Project Memory: Hebrew Handwriting OCR Backend (with Kraken)

## 🗂️ Project Purpose
Build a backend for an OCR system focused on **Hebrew handwriting**, including **connected script** and **Assyrian-style scripts** (Sephardic, Ashkenazi). The system supports:
- Uploading handwriting images
- Running OCR with Kraken
- User feedback to correct results
- Fine-tuning Kraken models per user
- Managing per-user model storage
- Full REST API and background training

---

## 🏗️ Architecture Summary

- **Framework**: FastAPI
- **OCR Engine**: Kraken
- **Database**: PostgreSQL (via SQLAlchemy)
- **Task Queue**: Celery + Redis
- **File Storage**: MinIO/S3-compatible
- **Orchestration**: Docker Compose (local environment)

---

## 📁 Folder Structure

app/
├── main.py # FastAPI entrypoint
├── models.py # SQLAlchemy DB models
├── routes/
│ ├── ocr.py # OCR-related API endpoints
│ ├── feedback.py # Feedback endpoints
│ └── projects.py # Project management
├── services/
│ ├── kraken_runner.py # Run/train Kraken
│ ├── storage.py # Upload/download from S3
│ └── feedback.py # Handle user corrections
├── celery_worker.py # Celery worker init
└── db.py # DB session handling


---

## 🧠 Function Responsibilities

- `run_ocr(image_path, model_path)`  
  → Uses Kraken to extract text from image using specified model.

- `train_model(user_id, dataset_path)`  
  → Trains or fine-tunes Kraken model with aligned image/text pairs.

- `save_feedback(user_id, image_id, corrected_text)`  
  → Stores user-corrected OCR results for training.

- `get_user_model(user_id)`  
  → Returns the most recent Kraken model for this user.

- `upload_image(image)`  
  → Stores image in S3 and creates new project entry in DB.

---

## 📡 API Endpoints (FastAPI)

| Method | Endpoint         | Description                   |
|--------|------------------|-------------------------------|
| POST   | /ocr/            | Upload image + run OCR        |
| POST   | /feedback/       | Submit corrected text         |
| POST   | /train/          | Trigger user model training   |
| GET    | /projects/{id}   | Retrieve OCR results          |

---

## 💡 Copilot Guidelines

- Prefer clarity over compactness.
- Never hardcode file paths; use config or environment variables.
- Separate concerns: Routes are thin, business logic lives in `services/`.
- Every `def` must have a docstring.
- Model training must be asynchronous (via Celery).
- Each user has a directory under `/models/{user_id}/`.

---

## 🧪 Feedback & Improvement

1. OCR is first run using a general `hebrew_base.mlmodel`.
2. User corrects result.
3. Corrections are saved.
4. Periodically (or by request), training is triggered.
5. New model is saved under the user’s model directory.
6. Future OCRs for that user use the fine-tuned model.

---

## 🔒 Security Notes

- Always validate image files (type & size).
- Feedback must be linked to a valid image + project.
- Model files must not be exposed directly over the API.

