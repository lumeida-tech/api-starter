import logging
import traceback
from http import HTTPStatus
from litestar import Request, Response
from litestar.exceptions import ValidationException, HTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Root exception for all domain errors."""


class NotFoundError(AppError):
    pass


class AlreadyExistsError(AppError):
    pass


class UnauthorizedError(AppError):
    pass


class ForbiddenError(AppError):
    pass


class ValidationError(AppError):
    pass


def _msg(content: str, status: int) -> Response:
    return Response(content={"message": content}, status_code=status)


def not_found_handler(_: Request, exc: NotFoundError) -> Response:
    return _msg(str(exc), HTTPStatus.NOT_FOUND)


def already_exists_handler(_: Request, exc: AlreadyExistsError) -> Response:
    return _msg(str(exc), HTTPStatus.CONFLICT)


def unauthorized_handler(_: Request, exc: UnauthorizedError) -> Response:
    return _msg(str(exc), HTTPStatus.UNAUTHORIZED)


def forbidden_handler(_: Request, exc: ForbiddenError) -> Response:
    return _msg(str(exc), HTTPStatus.FORBIDDEN)


def domain_validation_handler(_: Request, exc: ValidationError) -> Response:
    return _msg(str(exc), HTTPStatus.UNPROCESSABLE_ENTITY)


def http_exception_handler(_: Request, exc: HTTPException) -> Response:
    return _msg(exc.detail, exc.status_code)


def litestar_validation_handler(_: Request, exc: ValidationException) -> Response:
    detail = exc.extra
    if isinstance(detail, list) and detail:
        first = detail[0]
        message = first.get("message", str(first)) if isinstance(first, dict) else str(first)
    else:
        message = exc.detail or "Données invalides"
    return _msg(message, HTTPStatus.UNPROCESSABLE_ENTITY)


def internal_error_handler(req: Request, exc: Exception) -> Response:
    logger.error("Unhandled exception on %s %s\n%s", req.method, req.url.path, traceback.format_exc())
    return _msg("Erreur interne du serveur", HTTPStatus.INTERNAL_SERVER_ERROR)


EXCEPTION_HANDLERS: dict = {
    NotFoundError:       not_found_handler,
    AlreadyExistsError:  already_exists_handler,
    UnauthorizedError:   unauthorized_handler,
    ForbiddenError:      forbidden_handler,
    ValidationError:     domain_validation_handler,
    HTTPException:       http_exception_handler,
    ValidationException: litestar_validation_handler,
    500:                 internal_error_handler,
}
