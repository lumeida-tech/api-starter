from datetime import datetime, timedelta, UTC
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from jose import jwt, JWTError
from jinja2 import Environment, FileSystemLoader

from core.settings import settings
from core.exceptions import UnauthorizedError
from core.mail import send_email
from features.auth.schemas import UserResponse
from features.auth.tables import User
from core.storage import public_url

_jinja = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=True,
)

_ph = PasswordHasher()


def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def create_access_token(user_id: str, email: str, role: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "email": email, "role": role, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise UnauthorizedError("Token invalide ou expiré")


def user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone or "",
        location=user.location or "",
        profile_picture=public_url(user.profile_picture) if user.profile_picture else "",
        created_at=user.created_at.strftime("%d %b. %Y") if user.created_at else "",
    )


# ── Email helpers ─────────────────────────────────────────────────────────────

def _render(template_name: str, **ctx) -> str:
    return _jinja.get_template(template_name).render(
        app_name=settings.APP_NAME,
        year=datetime.now().year,
        **ctx,
    )


async def send_reset_password_email(to_email: str, reset_url: str) -> None:
    await send_email(
        to=to_email,
        subject=f"Réinitialisation de votre mot de passe — {settings.APP_NAME}",
        text=f"Réinitialisez votre mot de passe : {reset_url}\n\nCe lien est valable 24h.",
        html=_render("reset_password.html", reset_url=reset_url),
    )
