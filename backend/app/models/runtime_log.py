from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RuntimeLog(Base):
    __tablename__ = "runtime_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    level: Mapped[str] = mapped_column(String(16), index=True)
    event: Mapped[str] = mapped_column(String(64), index=True)
    message: Mapped[str] = mapped_column(Text)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
