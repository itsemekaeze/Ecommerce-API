from src.database.core import Base
from sqlalchemy import Column, Integer, String,DateTime,ForeignKey, Text, Boolean, Float
from sqlalchemy.orm  import relationship
from datetime import datetime


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    image_url = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    seller = relationship("User", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    

