from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class QueryRequest(BaseModel):
    """
    Represents a request to query a database table."""
    table: str
    fields: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
