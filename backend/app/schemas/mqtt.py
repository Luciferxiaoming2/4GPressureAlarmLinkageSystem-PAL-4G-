from pydantic import BaseModel, Field


class MqttStatusMessage(BaseModel):
    serial_number: str = Field(min_length=1, max_length=128)
    module_code: str = Field(min_length=1, max_length=32)
    is_online: bool
    relay_state: bool | None = None
    battery_level: int | None = Field(default=None, ge=0, le=100)
    voltage_value: float | None = None
    trigger_alarm_type: str | None = Field(default=None, max_length=32)
    alarm_message: str | None = None
