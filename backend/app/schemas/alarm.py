from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AlarmRecordCreate(BaseModel):
    module_id: int
    alarm_type: str = Field(min_length=1, max_length=32)
    message: str | None = None


class AlarmRecordRecover(BaseModel):
    recovered_at: datetime | None = None


class AlarmRecordRead(BaseModel):
    id: int
    module_id: int
    alarm_type: str
    alarm_status: str
    message: str | None
    triggered_at: datetime
    recovered_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
