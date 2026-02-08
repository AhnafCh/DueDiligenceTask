import sys
import importlib

required_packages = [
    "PyPDF2",
    "docx",
    "openpyxl",
    "pptx",
    "faiss",
    "langchain_text_splitters",
    "google.generativeai"
]

missing = []

for package in required_packages:
    try:
        importlib.import_module(package)
        print(f"[OK] {package}")
    except ImportError:
        print(f"[MISSING] {package}")
        missing.append(package)

if missing:
    print(f"\nMissing packages: {', '.join(missing)}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)
else:
    print("\nAll dependencies installed.")
    sys.exit(0)
