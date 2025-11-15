from src.database.core import Base
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, ForeignKey
from sqlalchemy.orm  import relationship


class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    categories = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True, index=True)
    original_price = Column(Numeric(10, 2))
    new_price = Column(Numeric(20, 2))
    percentage_discount = Column(Integer)
    offer_expiration_date = Column(DateTime(timezone=True), server_default=func.now())
    product_image = Column(String, nullable=False, server_default="productDefault.jpg")

    profile_id = Column(Integer, ForeignKey("business.id"), nullable=False)

    business = relationship("BusinessModel", back_populates="products")
    

