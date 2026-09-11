from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.config.database import Base

class PositionCompetence(Base):
    __tablename__ = "position_competence"
    
    position_id = Column(Integer, ForeignKey("position.id"), primary_key=True, nullable=False)
    competence_id = Column(Integer, ForeignKey("competence.id"), primary_key=True,nullable=False)
    expected_level = Column(Integer, nullable=False)
    
    position = relationship("Position")
    competence = relationship("Competence")
