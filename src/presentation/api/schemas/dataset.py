from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateDatasetRequest(BaseModel):
    name: str
    file_path: str
    source_type: str


class DatasetResponse(BaseModel):
    id: str
    name: str
    file_path: str
    source_type: str
    created_at: datetime
    auto_etl_run_id: Optional[str] = None
