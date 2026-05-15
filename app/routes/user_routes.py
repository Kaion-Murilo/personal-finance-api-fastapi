from fastapi import APIRouter, Depends, Request, Form
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
    """Abre uma sessão com o banco e garante o fechamento ao final da requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── API JSON ──────────────────────────────────────────

@router.get("/me", response_model=UsuarioResponse)
def me(current_user=Depends(get_current_user_api)):
    """Retorna os dados do usuário autenticado via token Bearer."""
    return current_user


@router.put("/me", response_model=UsuarioResponse)
def atualizar_me(
    nome: str,
    email: str,
    password_hash: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_api)
):
    """
    Atualiza os dados do usuário autenticado.
    A senha só é alterada se password_hash for informado.
    O usuário só pode editar a própria conta — id vem do token.
    """
    return UsuarioRepositorio.editar_usuario(db, current_user.id, nome, email, password_hash)


@router.delete("/me")
def deletar_me(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_api)
):
    """
    Remove permanentemente a conta do usuário autenticado.
    Operação irreversível — não há confirmação adicional na API.
    """
    UsuarioRepositorio.deletar_usuario(db, current_user.id)
    return {"message": "Conta excluída com sucesso"}


# ── FRONT HTML ────────────────────────────────────────

@front_router.get("/")
def perfil(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Exibe a tela de perfil com os dados do usuário logado para edição."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={
            "current_user": current_user,
            "request": request
        }
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
    """
    Processa o formulário de edição de perfil.
    password_hash vazio é convertido para None — mantém a senha atual
    sem exigir que o usuário redigite a senha para atualizar outros dados.
    """
    if isinstance(current_user, RedirectResponse):
        return current_user

    # string vazia do formulário vira None para não re-hashear sem necessidade
    UsuarioRepositorio.editar_usuario(db, current_user.id, nome, email, password_hash or None)
    return RedirectResponse(url="/user", status_code=303)


@front_router.post("/deletar")
def deletar_usuario(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Exclui a conta do usuário logado e encerra a sessão.
    Remove o cookie do token para garantir que o navegador não
    tente reutilizar um token de uma conta que não existe mais.
    """
    if isinstance(current_user, RedirectResponse):
        return current_user

    UsuarioRepositorio.deletar_usuario(db, current_user.id)

    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response