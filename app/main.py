from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

app = FastAPI(
    title="Personal Finance API",
    description="REST API for personal finance management built with FastAPI, featuring JWT authentication, PostgreSQL, and monthly financial reports.",
    version="1.0.0",
)
@app.get("/health")
async def health_check():
    return {"status": "OK"}

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )