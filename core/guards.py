from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler
from litestar.exceptions import NotAuthorizedException

from features.auth.helpers import decode_token

COOKIE_NAME = "access_token"


def _get_payload(connection: ASGIConnection) -> dict:
    token = connection.cookies.get(COOKIE_NAME)
    if not token:
        raise NotAuthorizedException("Non authentifié")
    try:
        return decode_token(token)
    except Exception:
        raise NotAuthorizedException("Token invalide ou expiré")


async def auth_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Vérifie que l'utilisateur est authentifié."""
    _get_payload(connection)
