from payment.domain.common.exceptions import AppError


class ApplicationError(AppError):
    @property
    def message(self) -> str:
        return "An application error occurred"
