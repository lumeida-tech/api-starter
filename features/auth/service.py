from features.auth.schemas import (
    LoginRequest, RegisterRequest, UserResponse, TokenResponse,
    UpdateProfileRequest, ChangePasswordRequest,
)


class AuthService:
    async def register(self, payload: RegisterRequest) -> UserResponse:
        raise NotImplementedError

    async def login(self, payload: LoginRequest) -> TokenResponse:
        raise NotImplementedError

    async def get_current_user(self, token: str) -> UserResponse:
        raise NotImplementedError

    async def forgot_password(self, email: str, redirect_url: str) -> None:
        raise NotImplementedError

    async def reset_password(self, reset_token: str, password: str) -> None:
        raise NotImplementedError

    async def update_profile(self, user_id: str, data: UpdateProfileRequest) -> UserResponse:
        raise NotImplementedError

    async def change_password(self, user_id: str, data: ChangePasswordRequest) -> None:
        raise NotImplementedError

    async def upload_avatar(self, user_id: str, content: bytes, filename: str, content_type: str) -> UserResponse:
        raise NotImplementedError
