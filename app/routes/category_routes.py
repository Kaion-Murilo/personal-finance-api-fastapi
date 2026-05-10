from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from app.banco_de_dados.database import SessionLocal
from app.banco_de_dados.category_repositorio import CategoryRepositorio
from app.auth.auth import get_current_user

router = APIRouter(prefix="/api/category", tags=["Categories API"])
front_router = APIRouter(prefix="/category", tags=["Categories Front"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def listar(db: Session = Depends(get_db)):
    return CategoryRepositorio.listar(db)

@front_router.get("/")
def listar_front(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    categorias = CategoryRepositorio.listar_por_usuario(db, current_user.id)
    return templates.TemplateResponse(
        request=request,
        name="categories.html",
        context={"categorias": categorias, "current_user": current_user}
    )

@front_router.post("/criar")
def criar(
    name: str = Form(...),
    description: str = Form(""),
    type: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    CategoryRepositorio.criar(db, name, description, type, current_user.id)
    return RedirectResponse(url="/category", status_code=303)

@front_router.post("/editar/{category_id}")
def editar(
    category_id: int,
    name: str = Form(...),
    description: str = Form(""),
    type: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    # garante que só edita categoria própria
    CategoryRepositorio.editar(db, category_id, name, description, type, current_user.id)
    return RedirectResponse(url="/category", status_code=303)

@front_router.post("/deletar/{category_id}")
def deletar(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    # garante que só deleta categoria própria
    CategoryRepositorio.deletar(db, category_id, current_user.id)
    return RedirectResponse(url="/category", status_code=303)