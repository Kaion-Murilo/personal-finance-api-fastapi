from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from app.banco_de_dados.database import SessionLocal
from app.banco_de_dados.category_repositorio import CategoryRepositorio
from app.auth.auth import get_current_user
from app.auth.api_auth import get_current_user_api
from app.schemas import CategoriaResponse, CategoriaCreate, CategoriaUpdate
from typing import List

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

# ── API JSON ──────────────────────────────────────────

@router.get("/", response_model=List[CategoriaResponse])
def listar(db: Session = Depends(get_db), current_user=Depends(get_current_user_api)):
    return CategoryRepositorio.listar_por_usuario(db, current_user.id)

@router.post("/", response_model=CategoriaResponse, status_code=201)
def criar_api(body: CategoriaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user_api)):
    return CategoryRepositorio.criar(db, body.name, body.description, body.type, current_user.id)

@router.put("/{category_id}", response_model=CategoriaResponse)
def editar_api(category_id: int, body: CategoriaUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user_api)):
    cat = CategoryRepositorio.editar(db, category_id, body.name, body.description, body.type, current_user.id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return cat

@router.delete("/{category_id}")
def deletar_api(category_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user_api)):
    cat = CategoryRepositorio.deletar(db, category_id, current_user.id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return {"message": "Categoria excluída com sucesso"}

# ── FRONT HTML ────────────────────────────────────────

@front_router.get("/")
def listar_front(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    categorias = CategoryRepositorio.listar_por_usuario(db, current_user.id)
    return templates.TemplateResponse(request=request, name="categories.html", context={"categorias": categorias, "current_user": current_user})

@front_router.post("/criar")
def criar(name: str = Form(...), description: str = Form(""), type: str = Form(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    CategoryRepositorio.criar(db, name, description, type, current_user.id)
    return RedirectResponse(url="/category", status_code=303)

@front_router.post("/editar/{category_id}")
def editar(category_id: int, name: str = Form(...), description: str = Form(""), type: str = Form(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    CategoryRepositorio.editar(db, category_id, name, description, type, current_user.id)
    return RedirectResponse(url="/category", status_code=303)

@front_router.post("/deletar/{category_id}")
def deletar(category_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    CategoryRepositorio.deletar(db, category_id, current_user.id)
    return RedirectResponse(url="/category", status_code=303)