from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Disease(Base):
    __tablename__ = "diseases"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)  # e.g. "tomato_early_blight"
    class_index: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_hi: Mapped[str] = mapped_column(String(200), nullable=False)
    name_pa: Mapped[str] = mapped_column(String(200), nullable=False)
    crop_en: Mapped[str] = mapped_column(String(100), nullable=False)
    crop_hi: Mapped[str] = mapped_column(String(100), nullable=False)
    crop_pa: Mapped[str] = mapped_column(String(100), nullable=False)
    description_en: Mapped[str] = mapped_column(Text, nullable=False)
    description_hi: Mapped[str] = mapped_column(Text, nullable=False)
    description_pa: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")  # "low" | "medium" | "high"

    treatments: Mapped[list["Treatment"]] = relationship("Treatment", back_populates="disease", lazy="select")  # noqa: F821
