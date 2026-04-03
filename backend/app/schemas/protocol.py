from pydantic import BaseModel, Field


class ProtocolTopicInfo(BaseModel):
    category: str
    serial_number: str | None = None
    module_code: str | None = None
    raw_topic: str


class RelayCommandPayload(BaseModel):
    serial_number: str
    module_code: str
    command_type: str = "relay_control"
    target_state: str = Field(pattern="^(open|closed)$")
    command_id: int
