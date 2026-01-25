from pydantic import BaseModel, Field
from typing import List, Optional

class ProcessRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Input text to process")
    context: Optional[str] = Field(None, description="Previous context (for smart completion)")

class SuggestionItem(BaseModel):
    text: str
    confidence: float
    type: str  # 'correction', 'completion', 'next_word'

class ResponseModel(BaseModel):
    original: str
    suggestions: List[SuggestionItem]
    sentiment: Optional[str] = None
