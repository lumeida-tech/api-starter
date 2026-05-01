from piccolo.conf.apps import AppConfig
from features.auth.tables import User, PasswordResetToken

APP_CONFIG = AppConfig(
    app_name="auth",
    migrations_folder_path="features/auth/migrations",
    table_classes=[User, PasswordResetToken],
)
