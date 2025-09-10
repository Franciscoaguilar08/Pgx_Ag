import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .core.config import APP_TITLE, OPENAI_API_KEY
from .core.database import cache_init
from .routers import analyze as analyze_router
from .routers import ai as ai_router
from .routers import export as export_router
from .services import civic_service, vep_service, oncokb_service, clinvar_service

app = FastAPI(title=APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# Static & templates
base_dir = os.path.dirname(os.path.dirname(__file__))
static_dir = os.path.join(base_dir, "static")
templates_dir = os.path.join(base_dir, "templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Routers
app.include_router(analyze_router.router)
app.include_router(ai_router.router)
app.include_router(export_router.router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_title": APP_TITLE})

@app.get("/health")
async def health():
    return {
        "ok": True,
        "ia": bool(OPENAI_API_KEY),
        "sources": {
            "CIViC": bool(civic_service.ping()),
            "VEP": bool(vep_service.ping()),
            "OncoKB": bool(oncokb_service.ping()),
            "ClinVar": bool(clinvar_service.ping()),
        }
    }

cache_init()

def get_app():
    return app
