from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .config import settings
from .db import Base, engine
from .models import User, RecommendationHistory
from .routers import auth, planners

BASE=Path(__file__).resolve().parent
Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name,version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.mount("/static",StaticFiles(directory=BASE/"static"),name="static")
templates=Jinja2Templates(directory=BASE/"templates")
app.include_router(auth.router); app.include_router(planners.router)

@app.get("/health")
def health(): return {"status":"ok","ai_enabled":settings.ai_enabled,"gemini_configured":bool(settings.gemini_api_key),"model":settings.gemini_model}

@app.get("/",response_class=HTMLResponse)
def index(request:Request): return templates.TemplateResponse("index.html",{"request":request})
@app.get("/login",response_class=HTMLResponse)
def login_page(request:Request): return templates.TemplateResponse("login.html",{"request":request})
@app.get("/register",response_class=HTMLResponse)
def register_page(request:Request): return templates.TemplateResponse("register.html",{"request":request})
@app.get("/dashboard",response_class=HTMLResponse)
def dashboard(request:Request): return templates.TemplateResponse("dashboard.html",{"request":request})
@app.get("/planner/{planner}",response_class=HTMLResponse)
def planner_page(request:Request,planner:str):
    if planner not in {"home","party","jewelry"}: return HTMLResponse("Planner not found",404)
    return templates.TemplateResponse(f"{planner}_planner.html",{"request":request,"planner":planner})
@app.get("/history",response_class=HTMLResponse)
def history_page(request:Request): return templates.TemplateResponse("history.html",{"request":request})
