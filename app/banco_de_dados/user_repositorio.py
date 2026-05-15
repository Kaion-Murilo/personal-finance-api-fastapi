from sqlalchemy.orm import Session
from app.models.user import UserTable
from app.banco_de_dados.base_repositorio import BaseRepositorio
from app.auth.auth import gerar_hash_senha
from typing import List, Optional


class UsuarioRepositorio(BaseRepositorio[UserTable]):
    """
    Repositório de usuários — acesso ao banco para operações CRUD.

    Métodos com sufixo _usuario são a implementação real.
    Métodos sem sufixo (listar, criar, editar, deletar) satisfazem o
    contrato do BaseRepositorio e delegam para os métodos com sufixo.
    """

    @staticmethod
    def listar(db: Session) -> List[UserTable]:
        """Satisfaz o contrato do BaseRepositorio — alias de listar_usuarios."""
        return db.query(UserTable).all()

    @staticmethod
    def listar_usuarios(db: Session) -> List[UserTable]:
        """Retorna todos os usuários — uso interno/administrativo."""
        return db.query(UserTable).all()

    @staticmethod
    def buscar_por_id(db: Session, id: int) -> Optional[UserTable]:
        """Busca um usuário pelo id. Retorna None se não encontrado."""
        return db.query(UserTable).filter(UserTable.id == id).first()

    @staticmethod
    def criar(db: Session, **kwargs) -> UserTable:
        """Satisfaz o contrato do BaseRepositorio — delega para criar_usuario."""
        return UsuarioRepositorio.criar_usuario(db, **kwargs)

    @staticmethod
    def criar_usuario(db: Session, nome: str, email: str, password_hash: str) -> UserTable:
        """
        Cria e persiste um novo usuário.
        A senha recebida é sempre convertida para hash antes de salvar —
        nunca armazena senha em texto puro no banco.
        """
        novo = UserTable(
            nome=nome,
            email=email,
            password_hash=gerar_hash_senha(password_hash)
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    @staticmethod
    def editar(db: Session, id: int, **kwargs) -> Optional[UserTable]:
        """Satisfaz o contrato do BaseRepositorio — delega para editar_usuario."""
        return UsuarioRepositorio.editar_usuario(db, id, **kwargs)

    @staticmethod
    def editar_usuario(
        db: Session,
        usuario_id: int,
        nome: str,
        email: str,
        password_hash: str = None
    ) -> Optional[UserTable]:
        """
        Atualiza os dados do usuário.
        A senha só é alterada se password_hash for fornecido — permite
        atualizar nome e email sem exigir nova senha do usuário.
        """
        usuario = db.query(UserTable).filter(UserTable.id == usuario_id).first()

        if usuario:
            usuario.nome = nome
            usuario.email = email

            # só re-hasheia se uma nova senha foi fornecida
            if password_hash:
                usuario.password_hash = gerar_hash_senha(password_hash)

            db.commit()
            db.refresh(usuario)

        return usuario

    @staticmethod
    def deletar(db: Session, id: int, **kwargs) -> Optional[UserTable]:
        """Satisfaz o contrato do BaseRepositorio — delega para deletar_usuario."""
        return UsuarioRepositorio.deletar_usuario(db, id)

    @staticmethod
    def deletar_usuario(db: Session, usuario_id: int) -> Optional[UserTable]:
        """
        Remove o usuário do banco permanentemente.
        Retorna o objeto deletado — útil para confirmar o que foi removido.
        Retorna None se o usuário não existir.
        """
        usuario = db.query(UserTable).filter(UserTable.id == usuario_id).first()

        if usuario:
            db.delete(usuario)
            db.commit()

        return usuario