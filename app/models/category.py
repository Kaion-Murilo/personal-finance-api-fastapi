from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Numeric
from datetime import datetime
from app.banco_de_dados.database import Base

class Categories(BaseModel):
    id_: int
    nome: str
    descricão: str
    type : str  # income | expense
    user_id: int
    created_at:str
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # income | expense
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    description = Column(String, nullable=True) 