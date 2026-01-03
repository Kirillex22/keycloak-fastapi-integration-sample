import httpx
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.dependencies import engine, get_current_user
from src.routers.auth import auth_router
from src.routers.posts import posts_router
from src.routers.users import users_router
from src.config import settings
from src.keycloak_client import KeycloakClient
from src.orm import Base

# Jinja2 templates directory
# Templates are located inside the `src` package
templates = Jinja2Templates(directory=str(Path(settings.BASE_DIR) / "src" / "templates"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client = httpx.AsyncClient()
    app.state.keycloak_client = KeycloakClient(http_client)

    # Ensure database directory exists (sqlite file cannot be created otherwise)
    db_file_dir = Path(settings.BASE_DIR) / "data"
    try:
        db_file_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # If directory creation fails, continue — engine will raise a clear error
        pass

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(posts_router, prefix="/api/posts", tags=["posts"])
app.include_router(users_router, prefix="/api/users", tags=["users"])

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory=str(Path(settings.BASE_DIR) / "src" / "templates" / "static")), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(StarletteHTTPException)
async def auth_exception_handler(request: Request, exc: StarletteHTTPException):
    # Redirect to Keycloak only on 401 (unauthenticated)
    if exc.status_code == 401:
        return RedirectResponse(
            f"{settings.auth_url}"
            f"?client_id={settings.CLIENT_ID}"
            f"&response_type=code"
            f"&scope=openid"
            f"&redirect_uri={settings.redirect_uri}"
        )
    # For other HTTP errors return a proper JSON response (avoid re-raising which caused 500s)
    return JSONResponse({"detail": exc.detail or "Error"}, status_code=exc.status_code)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Public landing page with login button
    return templates.TemplateResponse("index.html", {"request": request, "user": None, "settings": settings})

@app.get("/protected", response_class=HTMLResponse)
async def protected_page(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "settings": settings})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="localhost", port=8000, reload=True)