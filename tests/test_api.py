from __future__ import annotations

import io

import httpx
import pytest


@pytest.fixture
def csv_content() -> str:
    return """Дата;Номер группы;ФИО;Оценка
11.03.2025;101Б;Иванов Иван Иванович;4
18.09.2024;102Б;Петров Пётр Петрович;2
26.09.2024;103М;Сидоров Сидор Сидорович;5
20.05.2025;103М;Иванов Иван Иванович;2
01.02.2025;101Б;Петров Пётр Петрович;2
09.10.2024;102Б;Сидоров Сидор Сидорович;2
18.05.2025;102Б;Иванов Иван Иванович;2
08.03.2025;101Б;Петров Пётр Петрович;2
30.03.2025;103М;Сидоров Сидор Сидорович;3
15.04.2025;101Б;Иванов Иван Иванович;2
"""


@pytest.fixture
def api_url() -> str:
    return "http://localhost:8000"


@pytest.mark.asyncio
async def test_health_check(api_url: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_url}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_upload_grades_success(api_url: str, csv_content: str) -> None:
    async with httpx.AsyncClient() as client:
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        response = await client.post(f"{api_url}/upload-grades", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["records_loaded"] > 0
        assert data["students"] > 0


@pytest.mark.asyncio
async def test_upload_grades_invalid_file(api_url: str) -> None:
    async with httpx.AsyncClient() as client:
        files = {"file": ("test.txt", io.BytesIO(b"test"), "text/plain")}
        response = await client.post(f"{api_url}/upload-grades", files=files)
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_grades_invalid_csv(api_url: str) -> None:
    async with httpx.AsyncClient() as client:
        files = {"file": ("test.csv", io.BytesIO(b"invalid,data\n1,2"), "text/csv")}
        response = await client.post(f"{api_url}/upload-grades", files=files)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_more_than_3_twos(api_url: str, csv_content: str) -> None:
    async with httpx.AsyncClient() as client:
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        await client.post(f"{api_url}/upload-grades", files=files)
        
        response = await client.get(f"{api_url}/students/more-than-3-twos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "full_name" in data[0]
            assert "count_twos" in data[0]
            assert data[0]["count_twos"] > 3


@pytest.mark.asyncio
async def test_less_than_5_twos(api_url: str, csv_content: str) -> None:
    async with httpx.AsyncClient() as client:
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        await client.post(f"{api_url}/upload-grades", files=files)
        
        response = await client.get(f"{api_url}/students/less-than-5-twos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "full_name" in data[0]
            assert "count_twos" in data[0]
            assert data[0]["count_twos"] < 5

