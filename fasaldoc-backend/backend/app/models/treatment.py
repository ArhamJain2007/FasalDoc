from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.base import Base


class Treatment(Base):
    __tablename__ = "treatments"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    disease_id: Mapped[str] = mapped_column(
        String(100), ForeignKey("diseases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)   # "organic" | "chemical"
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_hi: Mapped[str] = mapped_column(String(200), nullable=False)
    name_pa: Mapped[str] = mapped_column(String(200), nullable=False)
    dosage: Mapped[str] = mapped_column(String(200), nullable=False)
    schedule: Mapped[str] = mapped_column(Text, nullable=False)

    disease: Mapped["Disease"] = relationship("Disease", back_populates="treatments")  # noqa: F821
