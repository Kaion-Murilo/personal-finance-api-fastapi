from sqlalchemy.orm import Session
from app.models.category import Category

class CategoryRepositorio:
    @staticmethod
    def listar(db: Session):
        return db.query(Category).all()

    @staticmethod
    def listar_por_usuario(db: Session, user_id: int):
        return db.query(Category).filter(Category.user_id == user_id).all()

    @staticmethod
    def criar(db: Session, name: str, description: str, type: str, user_id: int):
        nova = Category(name=name, description=description, type=type, user_id=user_id)
        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova

    @staticmethod
    def editar(db: Session, category_id: int, name: str, description: str, type: str, user_id: int):
        # filtra por id E user_id — impede editar categoria de outro usuário
        cat = db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id
        ).first()
        if cat:
            cat.name = name
            cat.description = description
            cat.type = type
            db.commit()
            db.refresh(cat)
        return cat

    @staticmethod
    def deletar(db: Session, category_id: int, user_id: int):
        # filtra por id E user_id — impede deletar categoria de outro usuário
        cat = db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id
        ).first()
        if cat:
            db.delete(cat)
            db.commit()
        return cat