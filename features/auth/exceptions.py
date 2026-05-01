from core.exceptions import UnauthorizedError, AlreadyExistsError, NotFoundError


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Email ou mot de passe invalide")


class UserAlreadyExistsError(AlreadyExistsError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Un compte existe déjà avec l'email '{email}'")


class UserNotFoundError(NotFoundError):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Utilisateur '{identifier}' introuvable")
