from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(String(2048), unique=True)
    retailer: Mapped[str] = mapped_column(String(30))
    target_price: Mapped[float] = mapped_column(Float)
    alert_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    alert_sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    current_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    observations: Mapped[list["PriceObservation"]] = relationship(cascade="all, delete-orphan", back_populates="product")
class PriceObservation(Base):
    __tablename__ = "price_observations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    price: Mapped[float] = mapped_column(Float)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    product: Mapped[Product] = relationship(back_populates="observations")
