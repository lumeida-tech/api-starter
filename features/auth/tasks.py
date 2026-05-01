from huey import cron
from core.worker import huey


@huey.task()
def send_reset_password_task(to_email: str, reset_url: str) -> None:
    """Envoie l'email de reset en arrière-plan."""
    import asyncio
    from features.auth.helpers import send_reset_password_email
    asyncio.run(send_reset_password_email(to_email, reset_url))


@huey.periodic_task(cron("0 3 * * *"))  # tous les jours à 3h
def cleanup_expired_tokens() -> None:
    """Supprime les tokens de reset expirés."""
    import asyncio
    from datetime import datetime, UTC
    from features.auth.tables import PasswordResetToken

    async def _run():
        await PasswordResetToken.delete().where(
            PasswordResetToken.expires_at < datetime.now(UTC)
        ).run()

    asyncio.run(_run())
