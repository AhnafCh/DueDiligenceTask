import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

text = "Hello world"
result = genai.embed_content(
    model="models/gemini-embedding-001",
    content=text,
    task_type="SEMANTIC_SIMILARITY"
)
embedding = result['embedding']
print(f"Embedding length: {len(embedding)}")
