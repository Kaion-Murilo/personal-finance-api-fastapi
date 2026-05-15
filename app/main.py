from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime

from app.banco_de_dados.database import Base, engine, SessionLocal
from app.models.user import UserTable
from app.models.category import Category
from app.models.transactions import Transaction
from app.routes.user_routes import router, front_router
from app.routes.category_routes import router as cat_router, front_router as cat_front_router
from app.routes.transaction_routes import router as trans_router, front_router as trans_front_router
from app.routes.auth_routes import router as auth_router
from app.auth.auth import get_current_user
from app.banco_de_dados.transaction_repositorio import TransactionRepositorio

# Caminho absoluto para templates — funciona independente de onde o uvicorn é executado
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app = FastAPI(
    title="Personal Finance API",
    description="REST API for personal finance management built with FastAPI, featuring JWT authentication, PostgreSQL, and monthly financial reports.",
    version="1.0.0",
)

# Arquivos estáticos servidos em /static — CSS, JS e imagens customizadas
app.mount("/static", StaticFiles(directory="static"), name="static")

# Cria as tabelas no banco se não existirem — seguro rodar múltiplas vezes
# Os models precisam estar importados acima para o create_all encontrá-los
Base.metadata.create_all(bind=engine)

# Popula o banco com dados iniciais — só executa se o banco estiver vazio
from app.seed import seed
seed()

# Rotas registradas em ordem: auth primeiro para garantir que /auth/login
# esteja disponível antes de qualquer rota protegida
app.include_router(auth_router)
app.include_router(trans_router)
app.include_router(trans_front_router)
app.include_router(router)
app.include_router(front_router)
app.include_router(cat_router)
app.include_router(cat_front_router)


def get_db():
    """Abre uma sessão com o banco e garante o fechamento ao final da requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
async def health_check():
    """Endpoint de healthcheck — usado pelo Docker e ferramentas de monitoramento."""
    return {"status": "OK"}


@app.get("/")
def home(request: Request, current_user=Depends(get_current_user)):
    """
    Dashboard principal — exibe resumo financeiro e últimas transações.
    Redireciona para o login se o token for inválido ou ausente.

    Carrega três conjuntos de dados para o dashboard:
    - resumo: totais de receitas, despesas e saldo
    - ultimas: 5 transações mais recentes
    - mensal: receitas e despesas mês a mês para o gráfico de barras
    """
    if isinstance(current_user, RedirectResponse):
        return current_user

    db = next(get_db())
    ano_atual = datetime.now().year

    resumo = TransactionRepositorio.resumo(db, current_user.id)
    ultimas = TransactionRepositorio.listar_por_usuario(db, current_user.id)[:5]
    mensal = TransactionRepositorio.resumo_mensal(db, current_user.id, ano_atual)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "versao": app.version,
            "current_user": current_user,
            "resumo": resumo,
            "ultimas": ultimas,
            "mensal": mensal,
            "ano_atual": ano_atual,
            "request": request
        }
    )