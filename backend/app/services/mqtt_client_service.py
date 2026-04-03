import asyncio
import json
import logging
from typing import Any

from paho.mqtt import client as mqtt_client

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.schemas.mqtt_client import MqttClientStatus
from app.services.logging_service import write_communication_log, write_runtime_log
from app.services.mqtt_adapter import process_mqtt_status_message
from app.services.protocol_service import build_relay_command_topic, parse_mqtt_topic

logger = logging.getLogger(__name__)


class MqttClientService:
    def __init__(self) -> None:
        self._client: mqtt_client.Client | None = None
        self._connected = False

    def status(self) -> MqttClientStatus:
        return MqttClientStatus(
            enabled=settings.MQTT_ENABLED,
            connected=self._connected,
            broker_host=settings.MQTT_BROKER_HOST,
            broker_port=settings.MQTT_BROKER_PORT,
            status_topic=settings.MQTT_STATUS_TOPIC,
        )

    def start(self) -> None:
        if not settings.MQTT_ENABLED:
            logger.info("MQTT 未启用，跳过客户端启动")
            return
        if self._client:
            return

        client = mqtt_client.Client(
            client_id=settings.MQTT_CLIENT_ID,
            protocol=mqtt_client.MQTTv311,
        )
        if settings.MQTT_USERNAME:
            client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message

        self._client = client
        try:
            client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=60)
            client.loop_start()
            logger.info("MQTT 客户端已启动，正在连接 %s:%s", settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT)
        except Exception as exc:
            logger.exception("MQTT 客户端启动失败: %s", exc)

    def stop(self) -> None:
        if not self._client:
            return
        self._client.loop_stop()
        self._client.disconnect()
        self._client = None
        self._connected = False
        logger.info("MQTT 客户端已停止")

    def _on_connect(
        self,
        client: mqtt_client.Client,
        _userdata: Any,
        _flags: dict,
        rc: int,
    ) -> None:
        self._connected = rc == 0
        if rc == 0:
            client.subscribe(settings.MQTT_STATUS_TOPIC)
            logger.info("MQTT 已连接并订阅主题 %s", settings.MQTT_STATUS_TOPIC)
        else:
            logger.error("MQTT 连接失败，返回码: %s", rc)

    def _on_disconnect(
        self,
        _client: mqtt_client.Client,
        _userdata: Any,
        rc: int,
    ) -> None:
        self._connected = False
        logger.warning("MQTT 已断开，返回码: %s", rc)

    def _on_message(
        self,
        _client: mqtt_client.Client,
        _userdata: Any,
        msg: mqtt_client.MQTTMessage,
    ) -> None:
        payload_text = msg.payload.decode("utf-8")
        asyncio.run(self._handle_status_message(msg.topic, payload_text))

    async def _handle_status_message(self, topic: str, payload_text: str) -> None:
        async with AsyncSessionLocal() as session:
            try:
                payload = json.loads(payload_text)
                topic_info = parse_mqtt_topic(topic)
                await process_mqtt_status_message(session, payload)
                await write_communication_log(
                    session,
                    channel="mqtt",
                    direction="inbound",
                    status="success",
                    device_serial=topic_info.serial_number or payload.get("serial_number"),
                    module_code=topic_info.module_code or payload.get("module_code"),
                    payload=payload,
                    message=f"processed mqtt topic {topic}",
                )
            except Exception as exc:
                await write_runtime_log(
                    session,
                    level="ERROR",
                    event="mqtt_message_error",
                    message=str(exc),
                    context={"topic": topic, "payload": payload_text},
                )
                logger.exception("MQTT 消息处理失败: %s", exc)

    def publish_relay_command(self, serial_number: str, module_code: str, payload: dict) -> dict:
        topic = build_relay_command_topic(serial_number, module_code)
        # 当前先返回将要发布的 topic/payload，真实 broker 可用后再切换为实际 publish。
        if self._client and self._connected:
            self._client.publish(topic, json.dumps(payload, ensure_ascii=False))
        return {"topic": topic, "payload": payload}


mqtt_client_service = MqttClientService()
