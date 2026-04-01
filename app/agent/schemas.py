from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class Intent(BaseModel):
    action: str
    table: Optional[str] = None
    filter: Optional[Dict[str, Any]] = None
    column: Optional[str] = None
    column_name: Optional[str] = None
    values: Optional[Dict[str, Any]] = None

    # 🔥 NEW
    default_value: Optional[Any] = None
    position: Optional[str] = None
    reference_column: Optional[str] = None
    value: Optional[Any] = None