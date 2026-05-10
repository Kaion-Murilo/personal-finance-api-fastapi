from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from app.banco_de_dados.database import SessionLocal
from app.banco_de_dados.transaction_repositorio import TransactionRepositorio
from app.banco_de_dados.category_repositorio import CategoryRepositorio
from app.auth.auth import get_current_user

router = APIRouter(prefix="/api/transaction", tags=["Transactions API"])
front_router = APIRouter(prefix="/transaction", tags=["Transactions Front"])

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
    return TransactionRepositorio.listar(db)

@front_router.get("/")
def listar_front(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    transacoes = TransactionRepositorio.listar_por_usuario(db, current_user.id)
    categorias = CategoryRepositorio.listar_por_usuario(db, current_user.id)
    return templates.TemplateResponse(
        request=request,
        name="transactions.html",
        context={"transacoes": transacoes, "categorias": categorias, "current_user": current_user}
    )

@front_router.post("/criar")
def criar(
    title: str = Form(...),
    amount: float = Form(...),
    date: str = Form(...),
    category_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    TransactionRepositorio.criar(db, title, amount, date, current_user.id, category_id)
    return RedirectResponse(url="/transaction", status_code=303)

@front_router.post("/editar/{transaction_id}")
def editar(
    transaction_id: int,
    title: str = Form(...),
    amount: float = Form(...),
    date: str = Form(...),
    category_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    TransactionRepositorio.editar(db, transaction_id, title, amount, date, current_user.id, category_id)
    return RedirectResponse(url="/transaction", status_code=303)

@front_router.post("/deletar/{transaction_id}")
def deletar(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    TransactionRepositorio.deletar(db, transaction_id, current_user.id)
    return RedirectResponse(url="/transaction", status_code=303)