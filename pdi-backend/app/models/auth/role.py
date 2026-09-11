from sqlalchemy import Column, Integer, String, ForeignKey
from app.config.database import Base

class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)