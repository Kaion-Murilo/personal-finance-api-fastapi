from pydantic import BaseModel, field_validator
from datetime import datetime, date
from typing import Optional


# ── Usuário ───────────────────────────────────────────

class UsuarioResponse(BaseModel):
    """Dados do usuário retornados pela API — nunca expõe o password_hash."""
    id: int
    nome: str
    email: str
    created_at: datetime

    class Config:
        # permite criar o DTO a partir de um model SQLAlchemy diretamente
        from_attributes = True


# ── Categoria ─────────────────────────────────────────

class CategoriaCreate(BaseModel):
    """Dados necessários para criar uma categoria."""
    name: str
    description: Optional[str] = ""
    type: str  # valores válidos: "income" | "expense"

    @field_validator("type")
    def validar_tipo(cls, v):
        """Rejeita valores inválidos antes de chegar no banco."""
        if v not in ["income", "expense"]:
            raise ValueError("Tipo deve ser 'income' ou 'expense'")
        return v


class CategoriaUpdate(BaseModel):
    """Dados necessários para atualizar uma categoria — mesmas regras do create."""
    name: str
    description: Optional[str] = ""
    type: str

    @field_validator("type")
    def validar_tipo(cls, v):
        if v not in ["income", "expense"]:
            raise ValueError("Tipo deve ser 'income' ou 'expense'")
        return v


class CategoriaResponse(BaseModel):
    """Dados da categoria retornados pela API."""
    id: int
    name: str
    description: Optional[str]
    type: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Transação ─────────────────────────────────────────

class TransacaoCreate(BaseModel):
    """Dados necessários para criar uma transação."""
    title: str
    amount: float
    date: date
    category_id: int

    @field_validator("amount")
    def validar_amount(cls, v):
        """Rejeita valores negativos ou zero — transação sem valor não faz sentido."""
        if v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        return v


class TransacaoUpdate(BaseModel):
    """Dados necessários para atualizar uma transação — mesmas regras do create."""
    title: str
    amount: float
    date: date
    category_id: int

    @field_validator("amount")
    def validar_amount(cls, v):
        if v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        return v


class TransacaoResponse(BaseModel):
    """Dados da transação retornados pela API."""
    id: int
    title: str
    amount: float
    date: date
    user_id: int
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Resumo ────────────────────────────────────────────

class ResumoResponse(BaseModel):
    """Resumo financeiro do usuário — usado no dashboard e na rota /api/transaction/resumo."""
    total_receitas: float
    total_despesas: float
    saldo: float
    total_transacoes: int


class ResumoCategoriaResponse(BaseModel):
    """Gasto agrupado por categoria — usado na rota /api/transaction/resumo/categorias."""
    categoria: str
    tipo: str
    total: float
    quantidade: int