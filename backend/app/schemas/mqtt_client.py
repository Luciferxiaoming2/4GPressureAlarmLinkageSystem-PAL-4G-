from pydantic import BaseModel


class MqttClientStatus(BaseModel):
    enabled: bool
    connected: bool
    broker_host: str
    broker_port: int
    status_topic: str
