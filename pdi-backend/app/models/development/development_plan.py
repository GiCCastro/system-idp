from datetime import date
import enum

from sqlalchemy import Column, Date, ForeignKey, Integer, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.config.database import Base

class PlanStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETE = "COMPLETE"

class DevelopmentPlan(Base):
    
    __tablename__ = "development_plan"
    id = Column(Integer, primary_key=True, autoincrement=True)
    development_id = Column(Integer, ForeignKey("development.id"), nullable=False)
    competence_id = Column(Integer, ForeignKey("competence.id"), nullable=False)
    gap = Column(Integer, nullable=False)
    action = Column(Text, nullable=False)
    created_at = Column(Date, default=date.today, nullable=False)
    development = relationship("Development")
    competence = relationship("Competence")
    status = Column(SQLEnum(PlanStatusEnum), nullable=False) 


 
