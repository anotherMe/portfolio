from pydantic import BaseModel, ConfigDict
from typing import Optional


class AccountBase(BaseModel):
    name: str
    description: Optional[str] = None


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
