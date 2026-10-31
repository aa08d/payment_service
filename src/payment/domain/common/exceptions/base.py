from typing import ClassVar


class AppError(Exception):
    status: ClassVar[int] = 500

    @property
    def message(self) -> str:
        return "An payment error occurred."


class DomainError(AppError):
    status: ClassVar[int] = 422

    @property
    def message(self) -> str:
        return str(self) or "A domain error occurred."
