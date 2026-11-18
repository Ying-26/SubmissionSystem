# db.py

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row


# PostgreSQL 資料庫連線設定
DATABASE_URL = "postgresql://postgres:941226@localhost:5432/mydb"


# FastAPI 啟動與關閉時管理資料庫連線池
@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.pool = AsyncConnectionPool(
        conninfo=DATABASE_URL,
        kwargs={"row_factory": dict_row},
        open=False
    )

    await app.state.pool.open()

    print("✅ PostgreSQL connected successfully")

    try:
        yield
    finally:
        await app.state.pool.close()
        print("🛑 PostgreSQL disconnected")


# 提供資料庫連線給各個 Router
async def getDB(request: Request):

    async with request.app.state.pool.connection() as conn:
        yield conn