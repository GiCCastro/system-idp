from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship  
from app.config.database import Base

class FormQuestion(Base):
    __tablename__ = "form_question"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False)
    competence_id = Column(Integer, ForeignKey("competence.id"), nullable=False)

    competence = relationship("Competence")