from fastapi import Depends, HTTPException, Request
from src.keycloak_client import KeycloakClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

#Получаем KeycloakClient из app.state
def get_keycloak_client(request: Request) -> KeycloakClient:
    return request.app.state.keycloak_client

  
#Получаем токен из cookie
async def get_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get("access_token")

  
#Получаем пользователя по токену
async def get_current_user(
    token: str = Depends(get_token_from_cookie),
    keycloak: KeycloakClient = Depends(get_keycloak_client),
) -> dict:
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized: No access token")

    try:
        user_info = await keycloak.get_user_info(token)
        return user_info
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")


# Создаем движок и фабрику сессий из конфигурации
from src.config import settings
engine = create_async_engine(settings.database_url, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency для получения сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session