from pydantic import BaseModel
from typing import Optional, Dict, Any

# Enforces structure, prevents garbage values from SLM

class Intent(BaseModel):
    action: str
    table: Optional[str] = None
    filter: Optional[Dict[str, Any]] = None
    column: Optional[str] = None
    column_name: Optional[str] = None
    values: Optional[Dict[str, Any]] = None