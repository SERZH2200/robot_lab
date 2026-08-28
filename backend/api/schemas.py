from __future__ import annotations

from pydantic import BaseModel, Field


class ProgramRunRequest(BaseModel):#проверка поля source, что это строка и не пустая
    source: str = Field(min_length=1)


class MazeLoadRequest(BaseModel):
    name: str = Field(min_length=1)
