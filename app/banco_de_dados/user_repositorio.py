from app.banco_de_dados.local import criar_banco
from app.models.user import User
from sqlalchemy.orm import Session
from app.models.user import UserTable
from app.auth.auth import gerar_hash_senha
from app.auth.auth import gerar_hash_senha
BancoDeDadosLocal  = criar_banco
class UsuarioRepositorio:
    @staticmethod
    def listar_usuarios(db: Session):
        return db.query(UserTable).all()
   


    @staticmethod
    def criar_usuario(db: Session, nome: str, email: str, password_hash: str):
        novo_usuario = UserTable(
            nome=nome,
            email=email,
            password_hash=gerar_hash_senha(password_hash)  # ← hash aqui
    )
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        return novo_usuario
    @staticmethod
    def criar_usuario(db: Session, nome: str, email: str, password_hash: str):
        novo_usuario = UserTable(
            nome=nome,
            email=email,
            password_hash=gerar_hash_senha(password_hash)  # ← hash aqui
        )
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        return novo_usuario
    @staticmethod
    def deletar_usuario(db: Session, usuario_id: int):
        usuario = db.query(UserTable).filter(UserTable.id == usuario_id).first()
        if usuario:
            db.delete(usuario)
            db.commit()
        return usuario
    from app.auth.auth import gerar_hash_senha

    @staticmethod
    def editar_usuario(db: Session, usuario_id: int, nome: str, email: str, password_hash: str = None):
        usuario = db.query(UserTable).filter(UserTable.id == usuario_id).first()
        if usuario:
            usuario.nome = nome
            usuario.email = email
            if password_hash:
                usuario.password_hash = gerar_hash_senha(password_hash)  # ← hash aqui
            db.commit()
            db.refresh(usuario)
        return usuario