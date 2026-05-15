from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.auth.auth import SECRET_KEY, ALGORITHM, get_db
from app.models.user import UserTable

# Esquema OAuth2 — aponta para a rota que gera o token
# O Swagger usa isso para exibir o botão Authorize no /docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Resposta padrão para qualquer falha de autenticação
# Centralizado aqui para não repetir em cada validação
_ERRO_NAO_AUTORIZADO = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token inválido ou expirado",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user_api(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Dependência para rotas da API REST — valida o token Bearer no header Authorization.
    Diferente do get_current_user (que usa cookie), esta função é usada nas rotas /api/.
    Uso: current_user=Depends(get_current_user_api)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")

        # token válido mas sem user_id — payload corrompido ou gerado por outro sistema
        if user_id is None:
            raise _ERRO_NAO_AUTORIZADO

    except JWTError:
        # cobre token expirado, assinatura inválida e formato incorreto
        raise _ERRO_NAO_AUTORIZADO

    usuario = db.query(UserTable).filter(UserTable.id == user_id).first()

    # usuário pode ter sido deletado após o token ser gerado
    if not usuario:
        raise _ERRO_NAO_AUTORIZADO

    return usuario