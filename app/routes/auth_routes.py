from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from app.auth.auth import verificar_senha, criar_token, get_db
from app.models.user import UserTable
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
router = APIRouter(prefix="/auth", tags=["Auth"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.post("/token")
def login_api(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = db.query(UserTable).filter(UserTable.email == form_data.username).first()
    if not usuario or not verificar_senha(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    token = criar_token(usuario.id, usuario.email)
    return {"access_token": token, "token_type": "bearer"}
@router.get("/login")
def tela_login(request: Request):
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
    usuario = db.query(UserTable).filter(UserTable.email == email).first()
    if not usuario or not verificar_senha(password, usuario.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"erro": "Email ou senha incorretos"}
        )
    token = criar_token(usuario.id, usuario.email)
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=3600)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response
@router.get("/cadastro")
def tela_cadastro(request: Request):
    return templates.TemplateResponse(request=request, name="cadastro.html", context={})

@router.post("/cadastro")
def fazer_cadastro(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # verifica se email já existe
    existente = db.query(UserTable).filter(UserTable.email == email).first()
    if existente:
        return templates.TemplateResponse(
            request=request,
            name="cadastro.html",
            context={"erro": "Email já cadastrado"}
        )

    from app.auth.auth import gerar_hash_senha
    from app.models.user import UserTable as UT
    novo = UserTable(nome=nome, email=email, password_hash=gerar_hash_senha(password))
    db.add(novo)
    db.commit()
    return RedirectResponse(url="/auth/login", status_code=302)