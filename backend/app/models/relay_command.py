from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RelayCommand(Base):
    __tablename__ = "relay_commands"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    alarm_record_id: Mapped[int | None] = mapped_column(
        ForeignKey("alarm_records.id"), index=True, nullable=True
    )
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), index=True)
    command_source: Mapped[str] = mapped_column(String(32), default="system")
    target_state: Mapped[str] = mapped_column(String(16))
    execution_status: Mapped[str] = mapped_column(String(32), default="pending")
    execution_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    alarm_record = relationship("AlarmRecord")
    module = relationship("Module", back_populates="relay_commands")
