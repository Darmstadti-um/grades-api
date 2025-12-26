from __future__ import annotations

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    status: str
    records_loaded: int = Field(ge=0)
    students: int = Field(ge=0)


class StudentTwos(BaseModel):
    full_name: str
    count_twos: int = Field(ge=0)
