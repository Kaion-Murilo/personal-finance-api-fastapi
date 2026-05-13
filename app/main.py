from fastapi import FastAPI, Request
from pathlib import Path
from fastapi.templating import Jinja2Templates
from app.banco_de_dados.database import Base
from app.routes import user_routes
from app.routes.category_routes import router as cat_router, front_router as cat_front_router
from fastapi.responses import HTMLResponse, RedirectResponse
from app.routes.user_routes import router, front_router
BASE_DIR = Path(__file__).resolve().parent.parent  # sobe de /app para a raiz do projeto
templates = Jinja2Templates(directory=BASE_DIR / "templates")
from app.banco_de_dados.database import Base, engine
from app.models.user import UserTable
from app.models.category import Category
from app.models.transactions import Transaction
from app.routes.transaction_routes import router as trans_router, front_router as trans_front_router
from app.routes.auth_routes import router as auth_router
from fastapi import APIRouter, Depends, Form, Request
app = FastAPI(
    title="Personal Finance API",
    description="REST API for personal finance management built with FastAPI, featuring JWT authentication, PostgreSQL, and monthly financial reports.",
    version="1.0.0",
)
Base.metadata.create_all(bind=engine)  



app.include_router(auth_router)
app.include_router(trans_router)
app.include_router(trans_front_router)
app.include_router(router)        
app.include_router(front_router) 
app.include_router(cat_router)
app.include_router(cat_front_router) 
@app.get("/health")
async def health_check():
    return {"status": "OK"}

from app.auth.auth import get_current_user
from fastapi.responses import RedirectResponse
from app.banco_de_dados.database import SessionLocal
from app.banco_de_dados.transaction_repositorio import TransactionRepositorio

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.get("/")
def home(request: Request, current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user

    db = next(get_db())
    resumo = TransactionRepositorio.resumo(db, current_user.id)
    ultimas = TransactionRepositorio.listar_por_usuario(db, current_user.id)[:5]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "versao": app.version,
            "current_user": current_user,
            "resumo": resumo,
            "ultimas": ultimas
        }
    )