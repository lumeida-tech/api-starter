from huey import RedisHuey
from core.settings import settings

huey = RedisHuey("app", url=settings.REDIS_URL)
