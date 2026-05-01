from redis.asyncio import Redis


def create_redis() -> Redis:
    return Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
        socket_timeout=1,
        socket_connect_timeout=1,
        max_connections=10,
    )