# Hebrew Text Recognition

A FastAPI application for Hebrew text recognition and OCR.

## Project Structure

```
├── app/
│   ├── crud.py                 # CRUD operations
│   ├── database.py             # Database configuration
│   ├── db.py                   # Database setup
│   ├── main.py                 # Main application entry point
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── routes/                 # API routes
│   │   ├── ocr.py              # OCR routes
│   │   └── projects.py         # Project routes
│   └── services/               # Service layer
│       ├── file_handler.py     # File handling services
│       └── user_project_service.py # User and project services
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

1. **CRUD Tests**: Testing database operations
2. **Model Tests**: Testing SQLAlchemy model relationships and constraints
3. **Route Tests**: Testing API endpoints
4. **Schema Tests**: Testing Pydantic schema validation

### Dependencies

- **FastAPI**: Modern API framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation
- **Pytest**: Testing framework
- **PostgreSQL**: Database (for production)
- **SQLite**: Database (for testing)
