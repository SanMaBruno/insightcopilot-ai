class DomainError(Exception):
    """Excepción base para errores del dominio."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
