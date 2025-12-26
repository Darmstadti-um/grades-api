from __future__ import annotations

import asyncpg
from fastapi import Request

from .settings import settings


async def create_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        dsn=settings.dsn,
        min_size=1,
        max_size=10,
        command_timeout=30,
    )


async def get_conn(request: Request):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        yield conn
