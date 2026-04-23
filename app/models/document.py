from pydantic import BaseModel
from typing import Optional

class Document(BaseModel):
    email: str
    filename: str
    visa_type: str      
    status: Optional[str] = "Pending"
    file_data: bytes
    submitted_date: Optional[str] = ""  # Made optional with default
    last_date: Optional[str] = ""        # Made optional with default