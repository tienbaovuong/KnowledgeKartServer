import aioredis
from app.settings.app_settings import AppSettings

app_settings = AppSettings()
redis = aioredis.from_url(app_settings.redis_dsn, max_connections=1000)
psub = redis.pubsub()
pub = aioredis.Redis.from_url(app_settings.redis_dsn, decode_responses=True)