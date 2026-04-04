from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RelayCommandCreate(BaseModel):
    module_id: int
    target_state: str = Field(pattern="^(open|closed)$")
    command_source: str = Field(default="manual_control", max_length=32)


class RelayCommandFeedback(BaseModel):
    execution_status: str = Field(pattern="^(dispatched|success|failed|queued)$")
    feedback_status: str = Field(default="acknowledged", max_length=32)
    feedback_message: str | None = None


class RelayCommandRead(BaseModel):
    id: int
    alarm_record_id: int | None
    module_id: int
    command_source: str
    target_state: str
    execution_status: str
    execution_result: str | None
    feedback_status: str | None
    feedback_message: str | None
    retry_count: int
    last_attempt_at: datetime | None
    executed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RelayRetryResult(BaseModel):
    total_scanned: int
    dispatched_count: int
    still_queued_count: int


class RelayCommandPage(BaseModel):
    total: int
    items: list[RelayCommandRead]
    limit: int
    offset: int
