from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.banco_de_dados.database import Base
class User(BaseModel):
    id_: int
    nome: str
    email: str
    password_hash : str
    created_at: str
class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)