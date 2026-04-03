from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RelayCommand(Base):
    __tablename__ = "relay_commands"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), index=True)
    command_source: Mapped[str] = mapped_column(String(32), default="system")
    target_state: Mapped[str] = mapped_column(String(16))
    execution_status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    module = relationship("Module", back_populates="relay_commands")
