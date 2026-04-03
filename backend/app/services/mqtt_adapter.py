from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.device import Device
from app.models.module import Module
from app.schemas.device import ModuleStatusReport
from app.schemas.mqtt import MqttStatusMessage
from app.services.device_service import update_module_status


def normalize_mqtt_status_payload(payload: dict) -> MqttStatusMessage:
    # 统一把外部 MQTT 消息归一成内部结构，后续不同协议只需要改这里。
    return MqttStatusMessage.model_validate(payload)


async def get_module_by_serial_and_code(
    db: AsyncSession,
    serial_number: str,
    module_code: str,
) -> Module | None:
    stmt = (
        select(Module)
        .join(Device, Module.device_id == Device.id)
        .options(selectinload(Module.device))
        .where(Device.serial_number == serial_number, Module.module_code == module_code)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def process_mqtt_status_message(
    db: AsyncSession,
    payload: dict,
) -> Module:
    message = normalize_mqtt_status_payload(payload)
    module = await get_module_by_serial_and_code(
        db=db,
        serial_number=message.serial_number,
        module_code=message.module_code,
    )
    if not module:
        raise ValueError("Module not found for incoming MQTT payload")

    # 真实接入 MQTT 时，最终仍复用统一的模块状态更新逻辑。
    updated_module = await update_module_status(
        db,
        module,
        ModuleStatusReport(
            is_online=message.is_online,
            source="mqtt_report",
            relay_state=message.relay_state,
            battery_level=message.battery_level,
            voltage_value=message.voltage_value,
            trigger_alarm_type=message.trigger_alarm_type,
            alarm_message=message.alarm_message,
        ),
    )
    return updated_module
