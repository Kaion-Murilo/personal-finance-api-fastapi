from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pathlib import Path
from app.auth.auth import verificar_senha, criar_token, gerar_hash_senha, get_db
from app.models.user import UserTable
from app.models.factories import TokenFactory

router = APIRouter(prefix="/auth", tags=["Auth"])

# Caminho absoluto para a pasta templates — funciona independente de onde
# o uvicorn é executado
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ── API JSON ──────────────────────────────────────────

@router.post("/token")
def login_api(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Rota de autenticação para a API REST — usada pelo Swagger e clientes externos.
    Recebe username (email) e password via form e retorna um token Bearer.
    """
    usuario = db.query(UserTable).filter(UserTable.email == form_data.username).first()

    # mensagem genérica intencional — não revela se o email existe ou não
    if not usuario or not verificar_senha(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    return TokenFactory.criar(usuario.id, usuario.email)


# ── FRONT HTML ────────────────────────────────────────

@router.get("/login")
def tela_login(request: Request):
    """
    Exibe a tela de login.
    Se o usuário já tiver um cookie válido, redireciona para o dashboard.
    """
    if request.cookies.get("access_token"):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(request=request, name="login.html", context={})


@router.post("/login")
def fazer_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Processa o login do formulário HTML.
    Em caso de sucesso, salva o token num cookie httponly e redireciona
    para o dashboard. httponly impede acesso via JavaScript — mais seguro.
    """
    usuario = db.query(UserTable).filter(UserTable.email == email).first()

    if not usuario or not verificar_senha(password, usuario.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"erro": "Email ou senha incorretos"}
        )

    token_data = TokenFactory.criar(usuario.id, usuario.email)
    response = RedirectResponse(url="/", status_code=302)

    # max_age em segundos — 3600 = 1 hora, alinhado com ACCESS_TOKEN_EXPIRE_MINUTES
    response.set_cookie(
        key="access_token",
        value=token_data["access_token"],
        httponly=True,
        max_age=3600
    )
    return response


@router.get("/logout")
def logout():
    """
    Encerra a sessão removendo o cookie do token.
    Redireciona para o login após o logout.
    """
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response


@router.get("/cadastro")
def tela_cadastro(request: Request):
    """Exibe o formulário de criação de conta."""
    return templates.TemplateResponse(request=request, name="cadastro.html", context={})


@router.post("/cadastro")
def fazer_cadastro(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Processa o cadastro de novo usuário.
    Verifica duplicidade de email antes de criar — email é único no banco.
    Após cadastro bem-sucedido, redireciona para o login.
    """
    existente = db.query(UserTable).filter(UserTable.email == email).first()

    if existente:
        return templates.TemplateResponse(
            request=request,
            name="cadastro.html",
            context={"erro": "Email já cadastrado"}
        )

    novo = UserTable(nome=nome, email=email, password_hash=gerar_hash_senha(password))
    db.add(novo)
    db.commit()

    return RedirectResponse(url="/auth/login", status_code=302)