from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RuntimeLogRead(BaseModel):
    id: int
    level: str
    event: str
    message: str
    context: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OperationLogRead(BaseModel):
    id: int
    actor_user_id: int | None
    action: str
    target_type: str
    target_id: int | None
    status: str
    detail: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommunicationLogRead(BaseModel):
    id: int
    channel: str
    direction: str
    device_serial: str | None
    module_code: str | None
    status: str
    payload: str | None
    message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuntimeLogPage(BaseModel):
    total: int
    items: list[RuntimeLogRead]


class OperationLogPage(BaseModel):
    total: int
    items: list[OperationLogRead]


class CommunicationLogPage(BaseModel):
    total: int
    items: list[CommunicationLogRead]


class LogsOverview(BaseModel):
    runtime_total: int
    runtime_error_count: int
    operation_total: int
    operation_failed_count: int
    communication_total: int
    communication_failed_count: int
