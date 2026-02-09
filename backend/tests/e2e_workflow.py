import httpx
import time
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Base URL for the API
BASE_URL = "http://localhost:8000"

def wait_for_api(timeout=30):
    """Wait for the API to be available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = httpx.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("API is up and running!")
                return True
        except httpx.RequestError:
            pass
        print("Waiting for API...")
        time.sleep(2)
    print("Timeout waiting for API.")
    return False

def upload_document(file_path):
    """Upload a document to the API."""
    print(f"Uploading {file_path}...")
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f)}
        response = httpx.post(f"{BASE_URL}/upload-document", files=files)
    response.raise_for_status()
    doc = response.json()
    print(f"Uploaded document. ID: {doc['id']}")
    return doc['id']

def index_document(doc_id):
    """Trigger indexing for a document."""
    print(f"Triggering indexing for {doc_id}...")
    response = httpx.post(f"{BASE_URL}/index-document-async", params={"document_id": doc_id})
    response.raise_for_status()
    data = response.json()
    print(f"Indexing queued. Request ID: {data['request_id']}")
    return data['request_id']

def poll_document_status(doc_id, target_status="READY", timeout=60):
    """Poll document status until it reaches target_status."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = httpx.get(f"{BASE_URL}/get-document-status", params={"document_id": doc_id})
        response.raise_for_status()
        status = response.json()["status"]
        print(f"Document status: {status}")
        if status == target_status:
            return True
        if status == "ERROR":
            print(f"Indexing failed: {response.json().get('error_message')}")
            return False
        time.sleep(5)
    print("Timeout waiting for indexing.")
    return False

def create_project(name, description="E2E Test Project"):
    """Create a new project."""
    print(f"Creating project: {name}...")
    payload = {
        "name": name,
        "description": description,
        "scope_type": "ALL_DOCS"
    }
    response = httpx.post(f"{BASE_URL}/create-project", json=payload)
    response.raise_for_status()
    project = response.json()
    print(f"Created project. ID: {project['id']}")
    return project['id']

def upload_questionnaire(project_id, file_path):
    """Upload a questionnaire to a project."""
    print(f"Uploading questionnaire {file_path} to project {project_id}...")
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f)}
        response = httpx.post(f"{BASE_URL}/{project_id}/questionnaire", files=files)
    response.raise_for_status()
    data = response.json()
    print(f"Questionnaire uploaded. Parsing queued. Request ID: {data['request_id']}")
    return data['request_id']

def poll_project_status(project_id, target_status="READY", timeout=60):
    """Poll project status until it reaches target_status."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = httpx.get(f"{BASE_URL}/get-project-status", params={"project_id": project_id})
        response.raise_for_status()
        status = response.json()["status"]
        print(f"Project status: {status}")
        if status == target_status:
            return True
        time.sleep(5)
    print("Timeout waiting for project parsing.")
    return False

def generate_answers(project_id):
    """Trigger answer generation for all questions in project."""
    print(f"Generating answers for project {project_id}...")
    response = httpx.post(f"{BASE_URL}/generate-all-answers", params={"project_id": project_id})
    response.raise_for_status()
    print("Bulk generation triggered.")
    return response.json()

def main():
    if not wait_for_api():
        sys.exit(1)

    # 1. Document Ingestion
    test_doc = "data/20260110_MiniMax_Accountants_Report.pdf"
    if not os.path.exists(test_doc):
        # Try local path relative to script
        test_doc = os.path.join(os.path.dirname(__file__), "../../data/20260110_MiniMax_Accountants_Report.pdf")
    
    doc_id = upload_document(test_doc)
    index_document(doc_id)
    if not poll_document_status(doc_id):
        print("Document indexing failed. Stopping E2E test.")
        sys.exit(1)

    # 2. Project Creation & Questionnaire Parsing
    project_id = create_project("E2E Test Project")
    questionnaire_doc = "data/ILPA_Due_Diligence_Questionnaire_v1.2.pdf"
    if not os.path.exists(questionnaire_doc):
        questionnaire_doc = os.path.join(os.path.dirname(__file__), "../../data/ILPA_Due_Diligence_Questionnaire_v1.2.pdf")
    
    upload_questionnaire(project_id, questionnaire_doc)
    if not poll_project_status(project_id):
        print("Project parsing failed. Stopping E2E test.")
        sys.exit(1)

    # 3. Answer Generation
    generate_answers(project_id)
    # Since answering is also async and may take time, we'd normally poll here too.
    # But for a basic E2E verification of flow triggers, this is a good start.
    print("E2E Workflow triggers completed successfully!")

if __name__ == "__main__":
    main()
