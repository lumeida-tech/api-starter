from piccolo.columns import Varchar, Boolean, Timestamptz, UUID, ForeignKey
from piccolo.table import Table


class User(Table, tablename="users"):
    id              = UUID(primary_key=True)
    email           = Varchar(length=255, unique=True, index=True)
    hashed_password = Varchar(length=255)
    full_name       = Varchar(length=255)
    role            = Varchar(length=50, default="user")   # admin | user
    phone           = Varchar(length=50, default="")
    location        = Varchar(length=255, default="")
    profile_picture = Varchar(length=500, default="")
    is_active       = Boolean(default=True)
    created_at      = Timestamptz(auto_now_add=True)


class PasswordResetToken(Table, tablename="password_reset_tokens"):
    id         = UUID(primary_key=True)
    user       = ForeignKey(references=User)
    token      = Varchar(length=255, unique=True, index=True)
    expires_at = Timestamptz()
    used_at    = Timestamptz(null=True, default=None)
    created_at = Timestamptz(auto_now_add=True)
