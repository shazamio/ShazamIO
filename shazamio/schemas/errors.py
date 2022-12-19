from dataclasses import dataclass


@dataclass
class ErrorModel:
    id: str
    title: str
    detail: str
    status: str
    code: str
