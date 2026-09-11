from sqlalchemy import Column, Integer, String
from app.config.database import Base

class Competence(Base):
    __tablename__ = "competence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(300), nullable=True)
    
