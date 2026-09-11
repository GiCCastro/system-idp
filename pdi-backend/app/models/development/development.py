import enum
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import date
from app.config.database import Base

class DevelopmentStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"

class Development(Base):
    
    __tablename__ = "development"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(Date, default=date.today, nullable=False)
    user = relationship("User")
    position = relationship("Position")
    status = Column(SQLEnum(DevelopmentStatusEnum), nullable=False) 

