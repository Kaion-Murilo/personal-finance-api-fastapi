from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.banco_de_dados.database import SessionLocal
from app.banco_de_dados.user_repositorio import UsuarioRepositorio
from app.auth.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["Users API"])
front_router = APIRouter(prefix="/user", tags=["Users Front"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def listar_usuarios(db: Session = Depends(get_db)):
    return UsuarioRepositorio.listar_usuarios(db)

@front_router.get("/")
def perfil(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={"current_user": current_user}
    )

@front_router.post("/editar")
def editar_usuario(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    password_hash: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    UsuarioRepositorio.editar_usuario(db, current_user.id, nome, email, password_hash or None)
    return RedirectResponse(url="/user", status_code=303)

@front_router.post("/deletar")
def deletar_usuario(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    UsuarioRepositorio.deletar_usuario(db, current_user.id)
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response