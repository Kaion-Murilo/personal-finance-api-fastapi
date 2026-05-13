from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.banco_de_dados.database import SessionLocal
from app.banco_de_dados.user_repositorio import UsuarioRepositorio
from app.auth.auth import get_current_user
from app.auth.api_auth import get_current_user_api
from app.schemas import UsuarioResponse

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

# ── API JSON ──────────────────────────────────────────

@router.get("/me", response_model=UsuarioResponse)
def me(current_user=Depends(get_current_user_api)):
    return current_user

@router.put("/me", response_model=UsuarioResponse)
def atualizar_me(
    nome: str,
    email: str,
    password_hash: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_api)
):
    return UsuarioRepositorio.editar_usuario(db, current_user.id, nome, email, password_hash)

@router.delete("/me")
def deletar_me(db: Session = Depends(get_db), current_user=Depends(get_current_user_api)):
    UsuarioRepositorio.deletar_usuario(db, current_user.id)
    return {"message": "Conta excluída com sucesso"}

# ── FRONT HTML ────────────────────────────────────────

@front_router.get("/")
def perfil(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return templates.TemplateResponse(request=request, name="users.html", context={"current_user": current_user})

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
def deletar_usuario(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    UsuarioRepositorio.deletar_usuario(db, current_user.id)
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response