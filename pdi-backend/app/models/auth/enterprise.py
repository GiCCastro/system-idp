from sqlalchemy import Column, Integer, String, ForeignKey
from app.config.database import Base

class Enterprise(Base):
    __tablename__ = "enterprise"

    id = Column(Integer, primary_key=True)
    cnpj = Column(String(14), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    niche = Column(String(255), nullable=True)