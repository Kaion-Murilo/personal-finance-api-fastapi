from app.banco_de_dados.local import criar_banco
from app.models.user import User
from sqlalchemy.orm import Session
from app.models.user import UserTable
BancoDeDadosLocal  = criar_banco

class UsuarioRepositorio:
    @staticmethod
    def listar_usuarios(db: Session):
        return db.query(UserTable).all()