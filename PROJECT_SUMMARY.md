# Hebrew Text Recognition

A FastAPI application for Hebrew text recognition and OCR, focusing on Hebrew handwriting including connected script and Assyrian-style scripts (Sephardic, Ashkenazi).

## Project Purpose

The system supports:
- Uploading handwriting images
- Running OCR with Kraken
- User feedback to correct results
- Fine-tuning Kraken models per user
- Managing per-user model storage
- Full REST API and background training

## Architecture

- **Framework**: FastAPI
- **OCR Engine**: Kraken
- **Database**: PostgreSQL (via SQLAlchemy)
- **Task Queue**: Celery + Redis
- **File Storage**: Simple File Server (local or network storage)
- **Orchestration**: Docker Compose (local environment)
- **Testing**: pytest with SQLite for test database

## Project Structure

```
├── app/
│   ├── crud.py                 # CRUD operations
│   ├── database.py             # Database configuration
│   ├── db.py                   # Database setup
│   ├── main.py                 # Main application entry point (FastAPI entrypoint)
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── routes/                 # API routes
│   │   ├── ocr.py              # OCR-related API endpoints
│   │   ├── feedback.py         # Feedback endpoints
│   │   └── projects.py         # Project management
│   ├── services/               # Service layer
│   │   ├── kraken_runner.py    # Run/train Kraken
│   │   ├── file_handler.py     # Upload/download files to simple file server
│   │   ├── feedback.py         # Handle user corrections
│   │   └── user_project_service.py # User and project services
│   └── celery_worker.py        # Celery worker init
├── tests/                      # Test directory
│   ├── crud/                   # CRUD tests
│   ├── models/                 # Model tests
│   ├── routes/                 # Route tests
│   └── schemas/                # Schema tests
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose for running the app
├── docker-compose.test.yml     # Docker Compose for running tests
├── pytest.ini                  # pytest configuration
├── requirements.txt            # Python dependencies
└── run_tests.sh                # Script to run tests
```

## Key Functionality

### Core Functions

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

### API Endpoints

| Method | Endpoint         | Description                   |
|--------|------------------|-------------------------------|
| POST   | /ocr/            | Upload image + run OCR        |
| POST   | /feedback/       | Submit corrected text         |
| POST   | /train/          | Trigger user model training   |
| GET    | /projects/{id}   | Retrieve OCR results          |

## Setup

### Prerequisites

- Docker and Docker Compose
- Git

### Running the Application

1. Clone the repository
2. Navigate to the project directory
3. Run the application with Docker Compose:

```bash
docker-compose up
```

The API will be available at http://localhost:8000

### API Documentation

When the application is running, you can access the Swagger documentation at:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Development

### Running Tests

To run the test suite, use the provided script:

```bash
./run_tests.sh
```

Or use Docker Compose directly:

```bash
docker-compose -f docker-compose.test.yml run --rm test
```

### Testing Strategy

The application uses pytest as the testing framework with the following test categories:

1. **Unit Tests**: Testing individual components in isolation
   - Focus on testing individual functions (e.g., in services/kraken_runner.py, crud.py)
   - Should be fast and cover various inputs and edge cases

2. **Integration Tests**: Testing interactions between components
   - Verify API endpoints correctly call service functions and interact with the database
   - Test the interaction between FastAPI routes, service logic, and database operations

3. **End-to-End Tests**: Simulate full user scenarios
   - Test entire system flows (e.g., upload -> OCR -> feedback -> training)
   - Cover key user journeys

4. **Test Organization**:
   - **CRUD Tests**: Testing database operations
   - **Model Tests**: Testing SQLAlchemy model relationships and constraints
   - **Route Tests**: Testing API endpoints
   - **Schema Tests**: Testing Pydantic schema validation

### Test Implementation Guidelines

- **Test Structure**: Organized in a `tests/` directory mirroring the `app/` structure
- **Clear Naming**: Tests have descriptive names (e.g., `test_run_ocr_success`)
- **Arrange-Act-Assert Pattern**: Setup, action, verification
- **Independent Tests**: Tests don't depend on state from previous tests
- **Fixtures**: Use pytest fixtures for test environments and dependencies
- **Database Testing**: Use dedicated test database or in-memory SQLite
- **Background Tasks**: Test Celery tasks by calling functions directly or using Celery's testing utilities

### OCR Workflow & Improvement

1. OCR is first run using a general `hebrew_base.mlmodel`
2. User corrects result
3. Corrections are saved
4. Periodically (or by request), training is triggered
5. New model is saved under the user's model directory
6. Future OCRs for that user use the fine-tuned model

## Security Considerations

- Always validate image files (type & size)
- Feedback must be linked to a valid image + project
- Model files must not be exposed directly over the API
- Each user has a separate model directory under `/models/{user_id}/`

## Development Guidelines

- Prefer clarity over compactness
- Never hardcode file paths; use config or environment variables
- Separate concerns: Routes are thin, business logic lives in `services/`
- Every function must have a docstring
- Model training must be asynchronous (via Celery)

## Dependencies

- **FastAPI**: Modern API framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation
- **Pytest**: Testing framework
- **PostgreSQL**: Database (for production)
- **SQLite**: Database (for testing)
- **Kraken**: OCR engine for Hebrew text recognition
- **Celery + Redis**: Task queue for asynchronous processing
