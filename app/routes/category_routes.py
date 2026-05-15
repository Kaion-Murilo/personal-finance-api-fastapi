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
    """Abre uma sessão com o banco e garante o fechamento ao final da requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── API JSON ──────────────────────────────────────────

@router.get("/", response_model=List[CategoriaResponse])
def listar(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_api)
):
    """Retorna todas as categorias do usuário autenticado via token Bearer."""
    return CategoryRepositorio.listar_por_usuario(db, current_user.id)


@router.post("/", response_model=CategoriaResponse, status_code=201)
def criar_api(
    body: CategoriaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_api)
):
    """
    Cria uma nova categoria vinculada ao usuário autenticado.
    O user_id vem do token — não é informado pelo cliente.
    """
    return CategoryRepositorio.criar(db, body.name, body.description, body.type, current_user.id)


@router.put("/{category_id}", response_model=CategoriaResponse)
def editar_api(
    category_id: int,
    body: CategoriaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_api)
):
    """
    Atualiza uma categoria do usuário autenticado.
    Retorna 404 se a categoria não existir ou não pertencer ao usuário.
    """
    cat = CategoryRepositorio.editar(db, category_id, body.name, body.description, body.type, current_user.id)

    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return cat


@router.delete("/{category_id}")
def deletar_api(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_api)
):
    """
    Remove uma categoria do usuário autenticado.
    Retorna 404 se a categoria não existir ou não pertencer ao usuário.
    """
    cat = CategoryRepositorio.deletar(db, category_id, current_user.id)

    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return {"message": "Categoria excluída com sucesso"}


# ── FRONT HTML ────────────────────────────────────────

@front_router.get("/")
def listar_front(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Exibe a tela de categorias com os dados do usuário logado.
    Redireciona para o login se o token for inválido ou ausente.
    """
    if isinstance(current_user, RedirectResponse):
        return current_user

    categorias = CategoryRepositorio.listar_por_usuario(db, current_user.id)

    return templates.TemplateResponse(
        request=request,
        name="categories.html",
        context={
            "categorias": categorias,
            "current_user": current_user,
            "request": request
        }
    )


@front_router.post("/criar")
def criar(
    name: str = Form(...),
    description: str = Form(""),
    type: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Processa o formulário de criação de categoria.
    O user_id vem do token — não é enviado pelo formulário.
    """
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
    """
    Processa o formulário de edição de categoria.
    O repositório filtra por user_id — impede editar categoria de outro usuário.
    """
    if isinstance(current_user, RedirectResponse):
        return current_user

    CategoryRepositorio.editar(db, category_id, name, description, type, current_user.id)
    return RedirectResponse(url="/category", status_code=303)


@front_router.post("/deletar/{category_id}")
def deletar(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Processa a exclusão de categoria via formulário HTML.
    O repositório filtra por user_id — impede deletar categoria de outro usuário.
    """
    if isinstance(current_user, RedirectResponse):
        return current_user

    CategoryRepositorio.deletar(db, category_id, current_user.id)
    return RedirectResponse(url="/category", status_code=303)