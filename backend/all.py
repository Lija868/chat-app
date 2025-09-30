from starlette.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from fastapi import FastAPI
from datetime import datetime
import os

from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

import settings
import user_api
from database import database, metadata

from dotenv import load_dotenv

load_dotenv()

def context_path(url):
    context_path = os.environ.get("APP_CONTEXT_PATH", "")
    return f"{context_path}{url}"

doc_path = os.environ.get("APP_DOC_PATH", None)

if doc_path is None:
    doc_path = context_path("/docs")

app = FastAPI(
    title=os.environ.get("APP_NAME", "llm-chat-starter-app"),
    version=os.environ.get("APP_VERSION", "1.0.0"),
    openapi_url=context_path("openapi.json"),
    docs_url=doc_path)

app.last_checks = datetime.now()

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()
    # create tables if using sqlite for quick start
    from sqlalchemy.ext.asyncio import create_async_engine
    engine = create_async_engine(os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db"), future=True)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


router = APIRouter(
    tags=["Health Check"],
    responses={
    }
)

@router.get("/heathcheck", )
def heartbeat():
    return "SUCCESS"

@router.get("/ping")
def ping():
    return "SUCCESS"

app.include_router(
    router,
    prefix=context_path(""),
)
app.include_router(
    user_api.router,
    prefix="",
)