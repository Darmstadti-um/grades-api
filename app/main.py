from __future__ import annotations

import csv
from io import StringIO
from typing import Any

import asyncpg
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from .db import create_pool, get_conn
from .schemas import StudentTwos, UploadResponse
from .validators import (
    CSV_DELIMITER,
    ParsedRow,
    validate_headers,
    parse_date,
    parse_group,
    parse_name,
    parse_grade,
)

app = FastAPI()


@app.on_event("startup")
async def _startup() -> None:
    app.state.db_pool = await create_pool()


@app.on_event("shutdown")
async def _shutdown() -> None:
    pool = getattr(app.state, "db_pool", None)
    if pool is not None:
        await pool.close()


def _decode_csv(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Cannot decode CSV")


def _iter_parsed_rows(csv_text: str) -> tuple[list[ParsedRow], list[dict[str, Any]]]:
    reader = csv.reader(StringIO(csv_text), delimiter=CSV_DELIMITER)
    try:
        headers = next(reader)
    except StopIteration:
        raise ValueError("CSV is empty")
    validate_headers(headers)

    dict_reader = csv.DictReader(StringIO(csv_text), delimiter=CSV_DELIMITER)

    rows: list[ParsedRow] = []
    errors: list[dict[str, Any]] = []

    for line_no, row in enumerate(dict_reader, start=2):
        try:
            rows.append(
                ParsedRow(
                    grade_date=parse_date(row.get("Дата")),
                    group_no=parse_group(row.get("Номер группы")),
                    full_name=parse_name(row.get("ФИО")),
                    grade=parse_grade(row.get("Оценка")),
                )
            )
        except Exception as e:
            errors.append({"line": line_no, "error": str(e), "raw": row})

    return rows, errors


async def _bulk_upsert_grades(conn: asyncpg.Connection, rows: list[ParsedRow]) -> int:
    await conn.execute("TRUNCATE TABLE grades_stage")

    records = ((r.grade_date, r.group_no, r.full_name, r.grade) for r in rows)
    await conn.copy_records_to_table(
        "grades_stage",
        records=records,
        columns=("grade_date", "group_no", "full_name", "grade"),
    )

    inserted = await conn.fetchval(
        """
        WITH ins AS (
            INSERT INTO grades (grade_date, group_no, full_name, grade)
            SELECT grade_date, group_no, full_name, grade
            FROM grades_stage
            ON CONFLICT (grade_date, group_no, full_name, grade) DO NOTHING
            RETURNING 1
        )
        SELECT COUNT(*)::int FROM ins
        """
    )
    return int(inserted or 0)


@app.post("/upload-grades", response_model=UploadResponse)
async def upload_grades(file: UploadFile = File(...), conn: asyncpg.Connection = Depends(get_conn)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    raw = await file.read()
    try:
        text = _decode_csv(raw)
        rows, errors = _iter_parsed_rows(text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if errors:
        raise HTTPException(status_code=422, detail={"message": "Validation failed", "errors": errors})

    if not rows:
        return UploadResponse(status="ok", records_loaded=0, students=0)

    async with conn.transaction():
        inserted = await _bulk_upsert_grades(conn, rows)

    students = len({r.full_name for r in rows})
    return UploadResponse(status="ok", records_loaded=inserted, students=students)


@app.get("/students/more-than-3-twos", response_model=list[StudentTwos])
async def students_more_than_3_twos(conn: asyncpg.Connection = Depends(get_conn)):
    sql = """
        SELECT full_name, COUNT(*) FILTER (WHERE grade = 2)::int AS count_twos
        FROM grades
        GROUP BY full_name
        HAVING COUNT(*) FILTER (WHERE grade = 2) > 3
        ORDER BY count_twos DESC, full_name
    """
    rows = await conn.fetch(sql)
    return [StudentTwos(full_name=r["full_name"], count_twos=r["count_twos"]) for r in rows]


@app.get("/students/less-than-5-twos", response_model=list[StudentTwos])
async def students_less_than_5_twos(conn: asyncpg.Connection = Depends(get_conn)):
    sql = """
        SELECT full_name, COUNT(*) FILTER (WHERE grade = 2)::int AS count_twos
        FROM grades
        GROUP BY full_name
        HAVING COUNT(*) FILTER (WHERE grade = 2) < 5
        ORDER BY count_twos, full_name
    """
    rows = await conn.fetch(sql)
    return [StudentTwos(full_name=r["full_name"], count_twos=r["count_twos"]) for r in rows]


@app.get("/health")
async def health(conn: asyncpg.Connection = Depends(get_conn)):
    await conn.fetchval("SELECT 1")
    return {"status": "ok"}
