from datetime import date
from typing import Annotated, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Status = Literal["applied", "interview", "offer", "rejected"]
STATUSES = get_args(Status)
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class JobIn(BaseModel):
    company: Text
    role: Text
    status: Status = "applied"
    applied_on: date = Field(default_factory=date.today)
    notes: str = ""


class JobOut(JobIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class Stats(BaseModel):
    total: int
    applied: int
    interview: int
    offer: int
    rejected: int
