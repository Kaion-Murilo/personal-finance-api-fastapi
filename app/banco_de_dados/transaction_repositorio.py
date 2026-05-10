from sqlalchemy.orm import Session
from app.models.transactions import Transaction

class TransactionRepositorio:
    @staticmethod
    def listar(db: Session):
        return db.query(Transaction).all()

    @staticmethod
    def listar_por_usuario(db: Session, user_id: int):
        return db.query(Transaction).filter(Transaction.user_id == user_id).all()

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
            Transaction.user_id == user_id  # impede editar transação de outro usuário
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
            Transaction.user_id == user_id  # impede deletar transação de outro usuário
        ).first()
        if t:
            db.delete(t)
            db.commit()
        return t