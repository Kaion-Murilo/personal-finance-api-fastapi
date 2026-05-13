from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Numeric
from datetime import datetime
from app.banco_de_dados.database import Base

class transaction(BaseModel):
    id_: int
    title: str
    amount: str
    date: str

    user_id: int 
    category_id : int

    created_at: str
from sqlalchemy.orm import relationship

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)
    date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category")  # ← adiciona isso