from enum import StrEnum, auto
from typing import Self

from pydantic import BaseModel


class MessageStatus(StrEnum):
    SUCCESS = auto()
    FAIL = auto()
    ERROR = auto()


class ResultMessage(BaseModel):
    status: MessageStatus
    message: str | None = None

    @classmethod
    def success(cls, message: str) -> Self:
        return cls(status=MessageStatus.SUCCESS, message=message)

    @classmethod
    def fail(cls, message: str) -> Self:
        return cls(status=MessageStatus.FAIL, message=message)

    @classmethod
    def error(cls, message: str) -> Self:
        return cls(status=MessageStatus.ERROR, message=message)
