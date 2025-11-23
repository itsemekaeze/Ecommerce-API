from sqlalchemy import Column, Integer, String
from src.database.core import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    public_id = Column(String, nullable=False)
