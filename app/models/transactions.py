
from pydantic import BaseModel

class transactions(BaseModel):
    id_: int
    titulo: str
    valor: str
    data: str
    user_id: int 
    categorie_id : int
    