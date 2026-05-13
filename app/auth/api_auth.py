from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.auth.auth import SECRET_KEY, ALGORITHM, get_db
from app.models.user import UserTable

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user_api(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise erro
    except JWTError:
        raise erro

    usuario = db.query(UserTable).filter(UserTable.id == user_id).first()
    if not usuario:
        raise erro
    return usuario