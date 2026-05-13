from fastapi import APIRouter, Depends, Form, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import date
from typing import List, Optional
from app.banco_de_dados.database import SessionLocal
from app.banco_de_dados.transaction_repositorio import TransactionRepositorio
from app.banco_de_dados.category_repositorio import CategoryRepositorio
from app.auth.auth import get_current_user
from app.auth.api_auth import get_current_user_api
from app.schemas import TransacaoResponse, TransacaoCreate, TransacaoUpdate

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

# ── API JSON ──────────────────────────────────────────
from app.schemas import ResumoResponse

# ── API JSON ──────────────────────────────────────────

@router.get("/resumo")
def resumo_api(
    data_inicio: Optional[date] = Query(None, description="Data inicial YYYY-MM-DD"),
    data_fim: Optional[date] = Query(None, description="Data final YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_api)
):
    return TransactionRepositorio.resumo(db, current_user.id, data_inicio, data_fim)

@router.get("/resumo/categorias")
def resumo_por_categoria_api(
    data_inicio: Optional[date] = Query(None, description="Data inicial YYYY-MM-DD"),
    data_fim: Optional[date] = Query(None, description="Data final YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_api)
):
    return TransactionRepositorio.resumo_por_categoria(db, current_user.id, data_inicio, data_fim)
    return TransactionRepositorio.resumo(db, current_user.id, data_inicio, data_fim)
@router.get("/", response_model=List[TransacaoResponse])
def listar(
    data_inicio: Optional[date] = Query(None, description="Filtrar a partir de (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Filtrar até (YYYY-MM-DD)"),
    category_id: Optional[int] = Query(None, description="Filtrar por categoria"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_api)
):
    return TransactionRepositorio.listar_por_usuario(db, current_user.id, data_inicio, data_fim, category_id)

@router.post("/", response_model=TransacaoResponse, status_code=201)
def criar_api(body: TransacaoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user_api)):
    return TransactionRepositorio.criar(db, body.title, body.amount, body.date, current_user.id, body.category_id)

@router.put("/{transaction_id}", response_model=TransacaoResponse)
def editar_api(transaction_id: int, body: TransacaoUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user_api)):
    t = TransactionRepositorio.editar(db, transaction_id, body.title, body.amount, body.date, current_user.id, body.category_id)
    if not t:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return t

@router.delete("/{transaction_id}")
def deletar_api(transaction_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user_api)):
    t = TransactionRepositorio.deletar(db, transaction_id, current_user.id)
    if not t:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return {"message": "Transação excluída com sucesso"}

# ── FRONT HTML ────────────────────────────────────────

@front_router.get("/")
def listar_front(
    request: Request,
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    category_id: Optional[str] = Query(None),  # ← str em vez de int
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    # converte para int só se tiver valor
    cat_id = int(category_id) if category_id and category_id.strip() else None

    transacoes = TransactionRepositorio.listar_por_usuario(db, current_user.id, data_inicio, data_fim, cat_id)
    categorias = CategoryRepositorio.listar_por_usuario(db, current_user.id)
    return templates.TemplateResponse(
        request=request,
        name="transactions.html",
        context={
            "transacoes": transacoes,
            "categorias": categorias,
            "current_user": current_user,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "category_id_filtro": cat_id
        }
    )

@front_router.post("/criar")
def criar(title: str = Form(...), amount: float = Form(...), date: str = Form(...), category_id: int = Form(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    TransactionRepositorio.criar(db, title, amount, date, current_user.id, category_id)
    return RedirectResponse(url="/transaction", status_code=303)

@front_router.post("/editar/{transaction_id}")
def editar(transaction_id: int, title: str = Form(...), amount: float = Form(...), date: str = Form(...), category_id: int = Form(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    TransactionRepositorio.editar(db, transaction_id, title, amount, date, current_user.id, category_id)
    return RedirectResponse(url="/transaction", status_code=303)

@front_router.post("/deletar/{transaction_id}")
def deletar(transaction_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    TransactionRepositorio.deletar(db, transaction_id, current_user.id)
    return RedirectResponse(url="/transaction", status_code=303)