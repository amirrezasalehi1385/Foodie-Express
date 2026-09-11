from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AdminActionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admin_id: int
    action: str
    target_type: str
    target_id: int | None
    description: str | None
    created_at: datetime