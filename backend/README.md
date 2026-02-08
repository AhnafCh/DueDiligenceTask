# Questionnaire Agent - Backend

## Phase 1: Foundation & Data Model ✅

This is the Phase 1 implementation of the Questionnaire Agent backend, providing the foundation and data model for the complete system.

## Project Structure

```
backend/
├── src/
│   ├── models/              # Pydantic schemas for all entities
│   │   ├── project.py       # Project, Section, Question models
│   │   ├── answer.py        # Answer, Citation, Confidence models
│   │   ├── document.py      # Document, Chunk, Index models
│   │   └── evaluation.py    # Evaluation, Similarity models
│   ├── api/
│   │   └── routes/          # FastAPI route definitions
│   │       ├── projects.py  # Project CRUD endpoints
│   │       ├── documents.py # Document upload and management
│   │       ├── answers.py   # Answer generation and review
│   │       ├── evaluation.py # Evaluation endpoints
│   │       └── status.py    # Status and health checks
│   ├── storage/             # Persistence layer
│   │   └── db/              # Database connection and models
│   │       ├── database.py  # SQLAlchemy setup
│   │       └── models.py    # ORM models
│   ├── workers/             # Async/background processing
│   │   ├── celery_app.py    # Celery configuration
│   │   └── tasks.py         # Async task definitions (stubs)
│   ├── utils/               # Shared helpers and constants
│   │   └── config.py        # Settings management
│   ├── services/            # Core business logic (placeholders)
│   └── indexing/            # Indexing pipeline (placeholders)
├── app.py                   # Main FastAPI application
├── requirements.txt         # Python dependencies
└── .env.example             # Environment configuration template
```

## Setup Instructions

### 1. Create Virtual Environment

**IMPORTANT**: All Python commands must be run within a virtual environment.

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# - DATABASE_URL: SQLite path (default is fine for development)
# - REDIS_URL: Redis connection string
# - CORS_ORIGINS: Frontend URLs
```

### 4. Run the Application

```powershell
# Development mode with auto-reload
python app.py

# Or using uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints (Phase 1)

### Projects
- `POST /projects/` - Create project
- `GET /projects/` - List projects
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project
- `POST /projects/{id}/create-async` - Async project creation (stub)
- `POST /projects/{id}/update-async` - Async project update (stub)
- `GET /projects/{id}/status` - Get project status

### Documents
- `POST /documents/` - Upload document
- `GET /documents/` - List documents
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document
- `POST /documents/{id}/index-async` - Async document indexing (stub)
- `GET /documents/{id}/status` - Get indexing status

### Answers
- `POST /answers/generate-single` - Generate single answer (stub)
- `POST /answers/generate-all` - Generate all answers (stub)
- `GET /answers/{id}` - Get answer details
- `PUT /answers/{id}` - Update/override answer
- `POST /answers/{id}/confirm` - Confirm AI answer
- `POST /answers/{id}/reject` - Reject with reason
- `POST /answers/{id}/flag-missing` - Flag missing data
- `GET /answers/{id}/history` - Get review history

### Evaluation
- `POST /evaluation/compare` - Compare AI vs human (stub)
- `GET /evaluation/project/{id}` - Get evaluation report (stub)
- `POST /evaluation/ground-truth` - Set ground truth (stub)

### Status
- `GET /requests/{request_id}` - Get async task status (stub)
- `GET /health` - Health check

## Data Models

### Core Entities

1. **Project**: Questionnaire project with sections and questions
   - Status: DRAFT, PROCESSING, READY, REVIEW, COMPLETED, OUTDATED
   - Scope: ALL_DOCS or SPECIFIC documents

2. **Section**: Logical grouping of questions within a project

3. **Question**: Individual question to be answered

4. **Answer**: AI-generated or manual answer with citations
   - Status: PENDING, CONFIRMED, REJECTED, MANUAL_UPDATED, MISSING_DATA
   - Created by: AI or HUMAN

5. **Citation**: Reference to source document chunk

6. **Document**: Uploaded reference document
   - Status: UPLOADED, INDEXING, READY, ERROR
   - Types: PDF, DOCX, XLSX, PPTX

7. **Chunk**: Text chunk from document with embeddings

8. **Evaluation**: Comparison between AI and human answers

9. **GroundTruth**: Human-verified correct answers

## Phase 1 Acceptance Criteria

- [x] All data models defined with relationships
- [x] Database schema created with SQLite
- [x] API endpoints respond with correct schemas
- [x] Development environment runs within `venv`
- [x] CORS middleware configured
- [x] Logging configured
- [x] Error handling implemented
- [x] Celery task queue configured (stubs)

## Next Steps (Phase 2)

Phase 2 will implement:
- Document parsing (PDF, DOCX, XLSX, PPTX)
- Text chunking with bounding boxes
- FAISS vector indexing
- Embedding generation
- Async document processing with Celery
- ALL_DOCS project invalidation

## Development Notes

- All async endpoints currently return stub responses
- Database is SQLite for development (will migrate to PostgreSQL for production)
- Redis is required for Celery (install and run locally)
- File uploads are stored in `uploads/` directory

## Testing

To test the API:

1. Start the server
2. Visit http://localhost:8000/docs
3. Try the following workflow:
   - Create a project
   - Upload a document
   - View project details
   - Update project status

## Redis Setup (for Celery)

Install Redis on Windows:
- Download from: https://github.com/microsoftarchive/redis/releases
- Or use Docker: `docker run -d -p 6379:6379 redis`

Start Redis:
```powershell
redis-server
```

Start Celery worker (in separate terminal with venv activated):
```powershell
celery -A src.core.celery_app worker --loglevel=info --pool=solo
```
