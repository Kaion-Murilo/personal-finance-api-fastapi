from fastapi import FastAPI, Request
from pathlib import Path
from fastapi.templating import Jinja2Templates
from app.routes import user_routes

from fastapi.responses import HTMLResponse, RedirectResponse
BASE_DIR = Path(__file__).resolve().parent.parent  # sobe de /app para a raiz do projeto
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app = FastAPI(
    title="Personal Finance API",
    description="REST API for personal finance management built with FastAPI, featuring JWT authentication, PostgreSQL, and monthly financial reports.",
    version="1.0.0",
)
from app.routes.user_routes import router, front_router

app.include_router(router)        # /api/user
app.include_router(front_router)  # /user  ← ESSE FALTAVA

@app.get("/health")
async def health_check():
    return {"status": "OK"}

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"versao": app.version}
    )