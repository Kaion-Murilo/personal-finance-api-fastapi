from pydantic import BaseModel

class User(BaseModel):
    id_: int
    nome: str
    email: str
    password_hash : str
    created_at: str