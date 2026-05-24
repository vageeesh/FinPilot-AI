import json
import redis.asyncio as aioredis
from app.core.config import settings


class RedisClient:
    def __init__(self):
        if settings.REDIS_URL:
            self.client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        else:
            self.client = aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
            )

    async def save_turn(self, key, user_msg, assistant_msg):
        """Save a conversation turn as a JSON string in Redis list."""
        turn = {
            "user": user_msg,
            "assistant": assistant_msg
        }

        await self.client.rpush(key, json.dumps(turn))

        # keep last N turns
        await self.client.ltrim(key, -settings.MAX_HISTORY, -1)

        # Setting the expiry time for the conversation history to 24 hours
        await self.client.expire(key, 86400)

    async def load_memory(self, key):
        """Load conversation history for the given key."""
        turns = await self.client.lrange(key, 0, -1)

        messages = []

        for t in turns:
            turn = json.loads(t)

            messages.append({
                "role": "user",
                "content": turn["user"]
            })

            messages.append({
                "role": "assistant",
                "content": turn["assistant"]
            })

        return messages

    async def clear_memory(self, key):
        await self.client.delete(key)