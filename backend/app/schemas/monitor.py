from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class MonitorCreate(BaseModel):
    name: str
    url: HttpUrl


class MonitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    is_active: bool
    created_at: datetime
