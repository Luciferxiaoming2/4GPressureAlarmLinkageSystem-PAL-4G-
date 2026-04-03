from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CommunicationLog(Base):
    __tablename__ = "communication_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    channel: Mapped[str] = mapped_column(String(32), index=True)
    direction: Mapped[str] = mapped_column(String(16), index=True)
    device_serial: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    module_code: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="success", index=True)
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
