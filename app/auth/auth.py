from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.banco_de_dados.database import SessionLocal
from app.models.user import UserTable
import os

# ── Configurações JWT ─────────────────────────────────
# SECRET_KEY deve estar no .env — nunca hardcoded no código
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Contexto de criptografia usando bcrypt
# deprecated="auto" garante migração automática se o algoritmo mudar
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    """Abre uma sessão com o banco e garante o fechamento ao final da requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Compara a senha digitada com o hash armazenado no banco."""
    return pwd_context.verify(senha_plana, senha_hash)


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash bcrypt da senha antes de salvar no banco."""
    return pwd_context.hash(senha)


def criar_token(user_id: int, email: str) -> str:
    """
    Cria um token JWT com o id e email do usuário.
    O token expira após ACCESS_TOKEN_EXPIRE_MINUTES minutos.
    """
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "user_id": user_id, "exp": expira}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Dependência para rotas HTML — lê o token do cookie e retorna o usuário logado.
    Se o token for inválido, expirado ou ausente, redireciona para o login.
    Uso: current_user=Depends(get_current_user)
    """
    token = request.cookies.get("access_token")

    # sem token — usuário não autenticado
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")

        # token válido mas sem user_id no payload — corrompido
        if user_id is None:
            return RedirectResponse(url="/auth/login", status_code=302)

    except JWTError:
        # token expirado ou assinatura inválida
        return RedirectResponse(url="/auth/login", status_code=302)

    usuario = db.query(UserTable).filter(UserTable.id == user_id).first()

    # usuário deletado após o token ser gerado
    if not usuario:
        return RedirectResponse(url="/auth/login", status_code=302)

    return usuario