import time
import httpx
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

BASE_URL = "http://localhost:8000"

def benchmark_ingestion(file_path):
    """Measure time taken for upload and indexing."""
    print(f"Starting benchmark for {file_path}...")
    
    # 1. Upload
    start_upload = time.time()
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f)}
        response = httpx.post(f"{BASE_URL}/upload-document", files=files)
    response.raise_for_status()
    doc_id = response.json()["id"]
    upload_time = time.time() - start_upload
    print(f"Upload time: {upload_time:.2f}s")
    
    # 2. Index
    start_index = time.time()
    httpx.post(f"{BASE_URL}/index-document-async", params={"document_id": doc_id})
    
    # Poll for status
    while True:
        resp = httpx.get(f"{BASE_URL}/get-document-status", params={"document_id": doc_id})
        status = resp.json()["status"]
        if status == "READY":
            break
        if status == "ERROR":
            print("Indexing failed!")
            return
        time.sleep(1)
    
    total_time = time.time() - start_upload
    index_time = time.time() - start_index
    
    print(f"Indexing time: {index_time:.2f}s")
    print(f"Total time: {total_time:.2f}s")
    return {
        "file": Path(file_path).name,
        "upload_s": upload_time,
        "index_s": index_time,
        "total_s": total_time
    }

def run_benchmarks():
    test_files = [
        "data/20260110_MiniMax_Accountants_Report.pdf",
        "data/ILPA_Due_Diligence_Questionnaire_v1.2.pdf"
    ]
    
    results = []
    for f in test_files:
        actual_path = f
        if not os.path.exists(actual_path):
            actual_path = os.path.join(os.getcwd(), "..", f)
            
        if os.path.exists(actual_path):
            res = benchmark_ingestion(actual_path)
            if res:
                results.append(res)
        else:
            print(f"File not found: {f} (tried {actual_path})")
    
    print("\n" + "="*40)
    print("BENCHMARK RESULTS")
    print("="*40)
    for r in results:
        print(f"File: {r['file']}")
        print(f"  Upload: {r['upload_s']:.2f}s")
        print(f"  Index:  {r['index_s']:.2f}s")
        print(f"  Total:  {r['total_s']:.2f}s")
        print("-" * 20)

if __name__ == "__main__":
    try:
        run_benchmarks()
    except Exception as e:
        print(f"Benchmark failed: {e}")
        print("Make sure the API is running at http://localhost:8000")
