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
- **File Storage**: Simple File Server (local or network storage)
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
│ ├── file_handler.py # Upload/download files to simple file server
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
  → Stores image using the simple file server and creates new project entry in DB.

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

---

## 🧪 Testing Policy

A comprehensive testing strategy is crucial to ensure the reliability, maintainability, and correctness of the Hebrew Handwriting OCR backend. The following policy outlines the types of tests, recommended frameworks, and general guidelines.

### Types of Tests

-   **Unit Tests**: Focus on testing individual components or functions in isolation (e.g., a single function in [`services/kraken_runner.py`](app/services/kraken_runner.py), a database query in [`crud.py`](app/crud.py)). These tests should be fast and cover various inputs and edge cases.
-   **Integration Tests**: Verify the interaction between different components (e.g., testing if an API endpoint correctly calls a service function and interacts with the database). This includes testing the integration of FastAPI routes with service logic, service logic with database operations, and potentially interactions with external services like Kraken (though mocking may be necessary for speed and reliability).
-   **End-to-End (E2E) Tests**: Simulate user scenarios to test the entire system flow, from receiving an image upload request to returning OCR results or triggering training. These tests are slower but provide high confidence in the system's overall functionality. They should cover key user journeys like image upload -> OCR -> feedback -> training.

### Testing Frameworks

-   **Pytest**: Recommended testing framework for Python. Provides a simple and flexible way to write and run tests, with extensive plugin support.
-   **Mock**: Use Python's built-in [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html) or `pytest-mock` for mocking external dependencies (like Kraken calls, file server interactions, or Celery tasks) in unit and integration tests.
-   **SQLAlchemy Test Helpers**: Utilize SQLAlchemy's testing utilities or libraries like `pytest-mock-alchemy` for testing database interactions without a live database connection where appropriate, or use test databases for integration tests.
-   **HTTPX/Requests**: For testing API endpoints, use libraries like `httpx` (recommended for FastAPI) or `requests` to make requests to the running application instance.

### General Guidelines

-   **Test Coverage**: Aim for high test coverage, particularly for critical business logic in the [`services/`](app/services/) and [`crud.py`](app/crud.py) modules.
-   **Test Structure**: Organize tests in a `tests/` directory mirroring the `app/` structure (e.g., `tests/services/`, `tests/routes/`).
-   **Clear Naming**: Test functions and files should have clear, descriptive names (e.g., `test_run_ocr_success`, `test_create_project_db`).
-   **Arrange-Act-Assert (AAA)**: Structure tests using the AAA pattern: Arrange (set up test data/environment), Act (perform the action being tested), Assert (verify the outcome).
-   **Independent Tests**: Tests should be independent and not rely on the state left by previous tests.
-   **Use Fixtures**: Leverage Pytest fixtures for setting up test environments, test data, and dependencies (like database sessions or mock objects).
-   **Asynchronous Testing**: Use `pytest-asyncio` for testing asynchronous code (FastAPI endpoints, async service functions).
-   **Database Testing**: For integration tests involving the database, use a dedicated test database or in-memory SQLite database where suitable. Ensure test data is cleaned up after each test or test suite.
-   **Background Tasks**: Test Celery tasks by either calling the task function directly (for unit tests) or by using Celery's testing utilities to ensure tasks are correctly queued and processed (for integration tests).
