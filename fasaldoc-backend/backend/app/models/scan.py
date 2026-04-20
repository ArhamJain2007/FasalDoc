from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, Float, Boolean, ForeignKey, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.base import Base


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    disease_class_index: Mapped[int] = mapped_column(Integer, nullable=False)
    disease_name: Mapped[str] = mapped_column(String(200), nullable=False)
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    stage: Mapped[str] = mapped_column(String(20), nullable=False)
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    treatment_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    synced_from_offline: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False, index=True)

    user: Mapped["User"] = relationship("User", back_populates="scans")  # noqa: F821
