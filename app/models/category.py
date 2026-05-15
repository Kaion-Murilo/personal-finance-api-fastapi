from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.banco_de_dados.database import Base


class Category(Base):
    """
    Model SQLAlchemy que representa a tabela 'categories' no banco.

    Cada categoria pertence a um usuário e classifica transações
    como receita (income) ou despesa (expense).
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False)  # valores válidos: "income" | "expense"
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)