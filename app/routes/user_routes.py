from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from app.banco_de_dados.database import SessionLocal
from app.banco_de_dados.user_repositorio import UsuarioRepositorio

router = APIRouter(prefix="/api/user", tags=["Users API"])
front_router = APIRouter(prefix="/user", tags=["Users Front"])
BASE_DIR = Path(__file__).resolve().parent.parent  # sobe de /app para a raiz do projeto
templates = Jinja2Templates(directory=BASE_DIR / "templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ ROTA API (aparece no /docs)
@router.get("/")
def listar_usuarios(db: Session = Depends(get_db)):
    return UsuarioRepositorio.listar_usuarios(db)

@front_router.get("/")
def listar_usuarios_front(request: Request, db: Session = Depends(get_db)):
    usuarios = UsuarioRepositorio.listar_usuarios(db)

    return templates.TemplateResponse(
    request,          # PRIMEIRO
    "users.html",     # SEGUNDO
    {
        "request": request,
        "usuarios": usuarios
    }
)