# Quick Start Guide - Phase 1

## Prerequisites

- Python 3.11 or higher
- Redis (for Celery)

## Setup Steps

### 1. Navigate to Backend Directory

```powershell
cd d:\InterviewTask\DueDiligenceTask\backend
```

### 2. Create and Activate Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment

```powershell
# Copy example environment file
Copy-Item .env.example .env

# The default settings in .env.example should work for local development
```

### 5. Initialize Database

```powershell
python init_db.py
```

Expected output:
```
INFO:__main__:Creating database tables...
INFO:__main__:✓ Database tables created successfully!
INFO:__main__:✓ Created 9 tables:
INFO:__main__:  - projects
INFO:__main__:  - sections
INFO:__main__:  - questions
INFO:__main__:  - answers
INFO:__main__:  - citations
INFO:__main__:  - documents
INFO:__main__:  - chunks
INFO:__main__:  - ground_truths
INFO:__main__:  - evaluations
```

### 6. Start the Application

```powershell
python app.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:__main__:Starting Questionnaire Agent API...
INFO:__main__:Database initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 7. Access the API

- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Testing the API

### Using the Interactive Docs (Recommended)

1. Open http://localhost:8000/docs in your browser
2. Try the following workflow:

#### Create a Project
1. Expand `POST /projects/`
2. Click "Try it out"
3. Use this example request body:
```json
{
  "name": "Test Project",
  "description": "My first project",
  "scope_type": "ALL_DOCS"
}
```
4. Click "Execute"
5. Note the `id` in the response

#### Upload a Document
1. Expand `POST /documents/`
2. Click "Try it out"
3. Choose a file to upload
4. Click "Execute"
5. Note the `id` in the response

#### Get Project Details
1. Expand `GET /projects/{project_id}`
2. Click "Try it out"
3. Enter the project ID from step 1
4. Click "Execute"

### Using cURL

```powershell
# Health check
curl http://localhost:8000/health

# Create a project
curl -X POST http://localhost:8000/projects/ `
  -H "Content-Type: application/json" `
  -d '{
    "name": "Test Project",
    "description": "My first project",
    "scope_type": "ALL_DOCS"
  }'

# List projects
curl http://localhost:8000/projects/
```

## Optional: Redis and Celery Setup

Redis and Celery are configured but not required for Phase 1 testing. They will be fully utilized in Phase 2.

### Install Redis (Windows)

**Option 1: Using Docker (Recommended)**
```powershell
docker run -d -p 6379:6379 redis
```

**Option 2: Native Installation**
Download from: https://github.com/microsoftarchive/redis/releases

### Start Celery Worker

In a separate terminal with venv activated:
```powershell
cd d:\InterviewTask\DueDiligenceTask\backend
.\venv\Scripts\Activate.ps1
celery -A src.core.celery_app worker --loglevel=info --pool=solo
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Make sure you're in the backend directory and venv is activated:
```powershell
cd d:\InterviewTask\DueDiligenceTask\backend
.\venv\Scripts\Activate.ps1
```

### Issue: Database errors

**Solution**: Re-initialize the database:
```powershell
# Delete the old database
Remove-Item questionnaire.db -ErrorAction SilentlyContinue

# Re-initialize
python init_db.py
```

### Issue: Port 8000 already in use

**Solution**: Change the port in .env:
```
API_PORT=8001
```

## Next Steps

Once Phase 1 is verified:
1. Review the API documentation at http://localhost:8000/docs
2. Test all CRUD endpoints
3. Proceed to Phase 2 implementation (Document Ingestion Pipeline)

## File Structure Verification

Your backend directory should look like this:

```
backend/
├── src/
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── answers.py
│   │       ├── documents.py
│   │       ├── evaluation.py
│   │       ├── projects.py
│   │       └── status.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── answer.py
│   │   ├── document.py
│   │   ├── evaluation.py
│   │   └── project.py
│   ├── __init__.py
│   └── tasks.py
├── venv/ (after setup)
├── uploads/ (created automatically)
├── .env (after setup)
├── .env.example
├── .gitignore
├── app.py
├── init_db.py
├── PHASE1_SUMMARY.md
├── README.md
└── requirements.txt
```

## Support

For issues or questions:
1. Check the logs in the terminal
2. Review PHASE1_SUMMARY.md for implementation details
3. Review README.md for comprehensive documentation
