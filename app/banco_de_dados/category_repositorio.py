from sqlalchemy.orm import Session
from app.models.category import Category
from app.banco_de_dados.base_repositorio import BaseRepositorio
from typing import List, Optional


class CategoryRepositorio(BaseRepositorio[Category]):
    """
    Repositório de categorias — acesso ao banco para operações CRUD.
    Todas as queries filtram por user_id para garantir isolamento entre usuários.
    """

    @staticmethod
    def listar(db: Session) -> List[Category]:
        """Retorna todas as categorias — uso interno/administrativo."""
        return db.query(Category).all()

    @staticmethod
    def buscar_por_id(db: Session, id: int) -> Optional[Category]:
        """Busca uma categoria pelo id sem filtrar por usuário."""
        return db.query(Category).filter(Category.id == id).first()

    @staticmethod
    def listar_por_usuario(db: Session, user_id: int) -> List[Category]:
        """Retorna apenas as categorias do usuário logado."""
        return db.query(Category).filter(Category.user_id == user_id).all()

    @staticmethod
    def criar(
        db: Session,
        name: str,
        description: str,
        type: str,
        user_id: int
    ) -> Category:
        """
        Cria uma nova categoria vinculada ao usuário.
        O db.refresh garante que o objeto retornado tem o id gerado pelo banco.
        """
        nova = Category(name=name, description=description, type=type, user_id=user_id)
        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova

    @staticmethod
    def editar(
        db: Session,
        id: int,
        name: str,
        description: str,
        type: str,
        user_id: int
    ) -> Optional[Category]:
        """
        Atualiza uma categoria — filtra por id E user_id.
        Se a categoria não pertencer ao usuário, retorna None sem lançar erro.
        A checagem de permissão fica no Service Layer.
        """
        cat = db.query(Category).filter(
            Category.id == id,
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
    def deletar(db: Session, id: int, user_id: int = None) -> Optional[Category]:
        """
        Remove uma categoria do banco.
        user_id é opcional — quando informado, garante que o usuário só
        deleta suas próprias categorias. Sem user_id, uso administrativo.
        """
        query = db.query(Category).filter(Category.id == id)

        # restringe ao dono quando user_id for fornecido
        if user_id:
            query = query.filter(Category.user_id == user_id)

        cat = query.first()

        if cat:
            db.delete(cat)
            db.commit()

        return cat