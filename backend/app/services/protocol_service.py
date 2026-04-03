from app.core.config import settings
from app.schemas.protocol import ProtocolTopicInfo, RelayCommandPayload


def parse_mqtt_topic(topic: str) -> ProtocolTopicInfo:
    # 先约定统一 topic 结构，后续如果设备真实协议不同，只改这里即可。
    parts = topic.split("/")
    if len(parts) >= 4 and parts[0] == "pal_4g":
        category = parts[1]
        serial_number = parts[2]
        module_code = parts[3]
        return ProtocolTopicInfo(
            category=category,
            serial_number=serial_number,
            module_code=module_code,
            raw_topic=topic,
        )
    return ProtocolTopicInfo(category="unknown", raw_topic=topic)


def build_relay_command_topic(serial_number: str, module_code: str) -> str:
    return f"{settings.MQTT_COMMAND_TOPIC_PREFIX}/{serial_number}/{module_code}"


def build_relay_command_payload(
    serial_number: str,
    module_code: str,
    target_state: str,
    command_id: int,
) -> RelayCommandPayload:
    # 真实设备接入前，先把业务命令统一映射成标准 payload 结构。
    return RelayCommandPayload(
        serial_number=serial_number,
        module_code=module_code,
        target_state=target_state,
        command_id=command_id,
    )
