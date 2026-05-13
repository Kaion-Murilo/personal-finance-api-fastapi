from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class CategoriaResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    type: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CategoriaCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    type: str  # income | expense

class CategoriaUpdate(BaseModel):
    name: str
    description: Optional[str] = ""
    type: str

class TransacaoResponse(BaseModel):
    id: int
    title: str
    amount: float
    date: date
    user_id: int
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TransacaoCreate(BaseModel):
    title: str
    amount: float
    date: date
    category_id: int

class TransacaoUpdate(BaseModel):
    title: str
    amount: float
    date: date
    category_id: int

class ResumoResponse(BaseModel):
    total_receitas: float
    total_despesas: float
    saldo: float
    total_transacoes: int

class ResumoCategoriaResponse(BaseModel):
    categoria: str
    tipo: str
    total: float
    quantidade: int