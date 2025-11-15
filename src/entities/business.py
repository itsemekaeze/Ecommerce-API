from src.database.core import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class BusinessModel(Base):
    __tablename__ = "business"
    id = Column(Integer, primary_key=True)
    business_name = Column(String, nullable=False, unique=True)
    city = Column(String, nullable=False, server_default="Unspecified")
    region = Column(String, nullable=False, server_default="Unspecified")
    business_description = Column(String, nullable=True)
    logo = Column(String, nullable=False, server_default="default.jpg")
    
    business_id = Column(Integer, ForeignKey("users.id"), unique=True)


    products = relationship("ProductModel", back_populates="business")