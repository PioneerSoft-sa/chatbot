from typing import List, Dict
import json

from app.config.redis_client import redis_client

def get_chat_key(user_id: str) -> str:
    return f"user_chat:{user_id}"

def check_chat_exists(user_id: str) -> bool:
    key = get_chat_key(user_id)
    return redis_client.exists(key)

def get_chat_history(user_id: str) -> List[Dict]:
    key = get_chat_key(user_id)
    raw = redis_client.get(key)
    if raw:
        return json.loads(raw)
    return []

def append_to_chat_history(user_id: str, message: Dict, CHAT_TTL_SECONDS: int = 60 * 10):
    history = get_chat_history(user_id)
    history.append(message)
    key = get_chat_key(user_id)
    redis_client.set(key, json.dumps(history))
    redis_client.expire(key, CHAT_TTL_SECONDS)

def clear_chat_history(user_id: str):
    key = get_chat_key(user_id)
    redis_client.delete(key)