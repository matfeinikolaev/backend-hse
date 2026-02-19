import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, field_validator, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Optional
import re
from datetime import date, datetime
import json
from pathlib import Path

NAME_REGEX = re.compile(r"^[А-Я][а-я]+$")

app = FastAPI()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


class Payload(BaseModel):
    first_name: str
    last_name: str
    birth_date: date
    cell_num: Optional[PhoneNumber] = None
    email: EmailStr

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not NAME_REGEX.match(value):
            raise ValueError(
                "Значение должно начинаться с заглавной буквы и содержать только буквы"
            )
        return value

    @field_validator("birth_date")
    @classmethod
    def check_not_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Дата не может быть в будущем")
        return value


@app.post("/gather/", response_model=Payload)
def gather(pl: Payload) -> Payload:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = DATA_DIR / f"record_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            pl.model_dump(),
            f,
            ensure_ascii=False,
            indent=4,
            default=str
        )

    return pl


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
