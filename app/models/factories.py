from datetime import datetime, timedelta
from jose import jwt
from app.auth.auth import SECRET_KEY, ALGORITHM

class TokenFactory:
    @staticmethod
    def criar(user_id: int, email: str, expires_minutes: int = 60) -> dict:
        expira = datetime.utcnow() + timedelta(minutes=expires_minutes)
        payload = {"sub": email, "user_id": user_id, "exp": expira}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}


class ResponseFactory:
    @staticmethod
    def sucesso(mensagem: str, dados: dict = None) -> dict:
        response = {"status": "success", "mensagem": mensagem}
        if dados:
            response["dados"] = dados
        return response

    @staticmethod
    def erro(mensagem: str, codigo: int = 400) -> dict:
        return {"status": "error", "mensagem": mensagem, "codigo": codigo}