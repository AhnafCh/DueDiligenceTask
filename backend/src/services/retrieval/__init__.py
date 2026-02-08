from pydantic import BaseModel
from typing import Optional, Dict, Any

class RetrievedChunk(BaseModel):
    id: str
    text: str
    score: float
    document_id: str
    filename: str
    page_number: Optional[int] = None
    bounding_box: Optional[Dict[str, Any]] = None
