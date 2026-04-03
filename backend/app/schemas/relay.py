from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RelayCommandRead(BaseModel):
    id: int
    alarm_record_id: int | None
    module_id: int
    command_source: str
    target_state: str
    execution_status: str
    execution_result: str | None
    retry_count: int
    last_attempt_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RelayRetryResult(BaseModel):
    total_scanned: int
    dispatched_count: int
    still_queued_count: int
