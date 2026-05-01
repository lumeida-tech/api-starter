from typing import Annotated

from litestar import Controller, post, get, delete, patch, Response, Request
from litestar.datastructures import Cookie, UploadFile
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body, Parameter

from core.settings import settings
from core.guards import auth_guard
from features.auth.schemas import (
    RegisterRequest, LoginRequest, UserResponse,
    ResetPasswordRequest, UpdateProfileRequest, ChangePasswordRequest,
)
from features.auth.service import AuthService

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def provide_auth_service() -> AuthService:
    return AuthService()


def _get_user_id(request: Request) -> str:
    from features.auth.helpers import decode_token
    token = request.cookies.get(COOKIE_NAME, "")
    return decode_token(token).get("sub", "")


class AuthController(Controller):
    path = "/auth"
    tags = ["Auth"]
    dependencies = {"auth_service": Provide(provide_auth_service, sync_to_thread=False)}

    @post("/register")
    async def register(self, data: RegisterRequest, auth_service: AuthService) -> Response[UserResponse]:
        user = await auth_service.register(data)
        return Response(content=user)

    @post("/login")
    async def login(self, data: LoginRequest, auth_service: AuthService) -> Response[UserResponse]:
        result = await auth_service.login(data)
        return Response(
            content=result.user,
            cookies=[
                Cookie(
                    key=COOKIE_NAME,
                    value=result.access_token,
                    httponly=True,
                    secure=settings.APP_ENV == "production",
                    samesite="lax",
                    max_age=COOKIE_MAX_AGE,
                    path="/",
                )
            ],
        )

    @get("/me", guards=[auth_guard])
    async def me(self, request: Request, auth_service: AuthService) -> UserResponse:
        token = request.cookies.get(COOKIE_NAME, "")
        return await auth_service.get_current_user(token)

    @delete("/logout", status_code=200)
    async def logout(self) -> Response[dict]:
        return Response(
            content={"message": "Déconnecté"},
            cookies=[Cookie(key=COOKIE_NAME, value="", httponly=True, max_age=0, path="/")],
        )

    @post("/forgot-password")
    async def forgot_password(
        self,
        email: Annotated[str, Parameter(query="email")],
        redirected_url: Annotated[str, Parameter(query="redirected_url")],
        auth_service: AuthService,
    ) -> dict:
        await auth_service.forgot_password(email, redirected_url)
        return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé."}

    @post("/reset-password")
    async def reset_password(
        self,
        token: Annotated[str, Parameter(query="token")],
        data: ResetPasswordRequest,
        auth_service: AuthService,
    ) -> dict:
        await auth_service.reset_password(token, data.password)
        return {"message": "Mot de passe réinitialisé avec succès."}


class UserController(Controller):
    path = "/users"
    tags = ["Users"]
    guards = [auth_guard]
    dependencies = {"auth_service": Provide(provide_auth_service, sync_to_thread=False)}

    @patch("/me")
    async def update_profile(self, data: UpdateProfileRequest, request: Request, auth_service: AuthService) -> UserResponse:
        return await auth_service.update_profile(_get_user_id(request), data)

    @patch("/me/password", status_code=200)
    async def change_password(self, data: ChangePasswordRequest, request: Request, auth_service: AuthService) -> dict:
        await auth_service.change_password(_get_user_id(request), data)
        return {"message": "Mot de passe mis à jour."}

    @post("/me/avatar")
    async def upload_avatar(
        self,
        data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
        request: Request,
        auth_service: AuthService,
    ) -> UserResponse:
        content = await data.read()
        return await auth_service.upload_avatar(
            _get_user_id(request),
            content,
            data.filename or "avatar",
            data.content_type or "image/jpeg",
        )
