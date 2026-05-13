from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transactions import Transaction
from datetime import date
from typing import Optional

class TransactionRepositorio:
    @staticmethod
    def listar(db: Session):
        return db.query(Transaction).all()

    @staticmethod
    def listar_por_usuario(
        db: Session,
        user_id: int,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        category_id: Optional[int] = None
    ):
        query = db.query(Transaction).filter(Transaction.user_id == user_id)
        if data_inicio:
            query = query.filter(Transaction.date >= data_inicio)
        if data_fim:
            query = query.filter(Transaction.date <= data_fim)
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        return query.order_by(Transaction.date.desc()).all()

    @staticmethod
    def criar(db: Session, title: str, amount: float, date: str, user_id: int, category_id: int):
        nova = Transaction(title=title, amount=amount, date=date, user_id=user_id, category_id=category_id)
        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova

    @staticmethod
    def editar(db: Session, transaction_id: int, title: str, amount: float, date: str, user_id: int, category_id: int):
        t = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()
        if t:
            t.title = title
            t.amount = amount
            t.date = date
            t.category_id = category_id
            db.commit()
            db.refresh(t)
        return t

    @staticmethod
    def deletar(db: Session, transaction_id: int, user_id: int):
        t = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()
        if t:
            db.delete(t)
            db.commit()
        return t

    @staticmethod
    def resumo(db: Session, user_id: int, data_inicio: Optional[date] = None, data_fim: Optional[date] = None):
        query = db.query(Transaction).filter(Transaction.user_id == user_id)
        if data_inicio:
            query = query.filter(Transaction.date >= data_inicio)
        if data_fim:
            query = query.filter(Transaction.date <= data_fim)

        transacoes = query.all()
        receitas = sum(float(t.amount) for t in transacoes if t.category.type == "income") if transacoes else 0
        despesas = sum(float(t.amount) for t in transacoes if t.category.type == "expense") if transacoes else 0

        return {
            "total_receitas": receitas,
            "total_despesas": despesas,
            "saldo": receitas - despesas,
            "total_transacoes": len(transacoes)
        }

    @staticmethod
    def resumo_por_categoria(db: Session, user_id: int, data_inicio: Optional[date] = None, data_fim: Optional[date] = None):
        query = db.query(Transaction).filter(Transaction.user_id == user_id)
        if data_inicio:
            query = query.filter(Transaction.date >= data_inicio)
        if data_fim:
            query = query.filter(Transaction.date <= data_fim)

        transacoes = query.all()
        categorias = {}
        for t in transacoes:
            nome = t.category.name
            tipo = t.category.type
            if nome not in categorias:
                categorias[nome] = {"categoria": nome, "tipo": tipo, "total": 0, "quantidade": 0}
            categorias[nome]["total"] += float(t.amount)
            categorias[nome]["quantidade"] += 1

        return list(categorias.values())