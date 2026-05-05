from pydantic import BaseModel

class Categories(BaseModel):
    id_: int
    nome: str
    descricão: str
    user_id:str