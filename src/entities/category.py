from src.database.core import Base
from sqlalchemy import Column, Integer, String, DateTime,  Text
from sqlalchemy.orm import relationship
from datetime import datetime


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship("Product", back_populates="category")