from http import HTTPStatus

from litestar import Litestar, get, Response
from litestar.config.cors import CORSConfig
from litestar.logging import LoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin

from core.settings import settings
from core.exceptions import EXCEPTION_HANDLERS
from core.storage import setup_bucket as setup_minio
from features.auth.controller import AuthController, UserController


@get("/health", tags=["Health"])
async def health_check() -> Response:
    return Response(
        content={"status": "ok", "service": settings.APP_NAME},
        status_code=HTTPStatus.OK,
    )


async def seed_admin() -> None:
    import logging
    from features.auth.tables import User
    from features.auth.helpers import hash_password

    logger = logging.getLogger(__name__)

    existing = await User.objects().where(User.email == settings.ADMIN_EMAIL).first()
    if existing:
        return

    admin = User(
        email=settings.ADMIN_EMAIL,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
        full_name=settings.ADMIN_NAME,
        role="admin",
    )
    try:
        await admin.save().run()
        logger.info(f"Compte admin créé : {settings.ADMIN_EMAIL}")
    except Exception:
        pass  # race condition entre workers — déjà inséré


logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={"standard": {"format": "%(asctime)s %(levelname)s %(name)s — %(message)s"}},
    log_exceptions="debug",
)

logging_middleware = LoggingMiddlewareConfig(
    request_log_fields=["method", "path", "query"],
    response_log_fields=["status_code"],
)

rate_limit = RateLimitConfig(
    rate_limit=("minute", 60),  # 60 requêtes / minute par IP
    exclude=["/health"],
)

app = Litestar(
    middleware=[logging_middleware.middleware, rate_limit.middleware],
    route_handlers=[
        health_check,
        AuthController,
        UserController,
        # Ajouter ici les controllers des nouvelles features
    ],
    on_startup=[seed_admin, setup_minio],
    exception_handlers=EXCEPTION_HANDLERS,
    logging_config=logging_config,
    cors_config=CORSConfig(
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
        allow_credentials=True,
    ),
    openapi_config=OpenAPIConfig(
        title=f"{settings.APP_NAME} API",
        version="1.0.0",
        path="/docs",
        render_plugins=[ScalarRenderPlugin()],
    ),
)
