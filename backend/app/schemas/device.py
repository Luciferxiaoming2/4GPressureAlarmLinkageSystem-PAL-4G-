from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ModuleCreate(BaseModel):
    module_code: str = Field(min_length=1, max_length=32)


class ModuleRead(BaseModel):
    id: int
    module_code: str
    relay_state: bool
    is_online: bool
    battery_level: int | None
    voltage_value: float | None
    last_seen_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    serial_number: str = Field(min_length=1, max_length=128)


class DeviceRead(BaseModel):
    id: int
    name: str
    serial_number: str
    status: str
    owner_id: int | None
    created_at: datetime
    updated_at: datetime
    modules: list[ModuleRead] = []

    model_config = ConfigDict(from_attributes=True)
