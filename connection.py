from redis_om import get_redis_connection

# Conexão com Redis
redis = get_redis_connection(
    host='redis-14317.c302.asia-northeast1-1.gce.cloud.redislabs.com',
    port='14317',
    password='9wSNCkb7ukgJNxosdTQjnQAY5U9ocab7',
    decode_responses=True
)
