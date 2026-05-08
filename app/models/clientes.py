from pydantic import BaseModel

class Cliente(BaseModel):
    id_: int
    nome: str
    email: str
    created_at: str