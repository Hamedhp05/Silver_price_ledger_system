from sqlalchemy import Column, String, Integer, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base

class SourceModel(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String,nullable=False)
    enabled = Column(Boolean, default=True)
    

    prices = relationship("PriceModel", back_populates="source")