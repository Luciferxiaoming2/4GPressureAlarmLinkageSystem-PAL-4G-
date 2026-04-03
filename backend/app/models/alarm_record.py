from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AlarmRecord(Base):
    __tablename__ = "alarm_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), index=True)
    alarm_type: Mapped[str] = mapped_column(String(32), index=True)
    alarm_status: Mapped[str] = mapped_column(String(32), default="triggered")
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    recovered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    module = relationship("Module", back_populates="alarm_records")
