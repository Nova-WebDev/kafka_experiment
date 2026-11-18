from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KL_")

    broker_ids: tuple[int, ...] = (1, 2, 3, 4, 5)
    broker_host_pattern: str = "kl_kafka_{broker_id}"
    broker_port: int = 9092

    topic_name: str = "orders"
    topic_partitions: int = 3
    topic_replication_factor: int = 5
    min_insync_replicas: int = 3

    cluster_poll_interval_seconds: float = 1.0
    broker_probe_timeout_seconds: float = 0.5
    kafka_request_timeout_seconds: float = 1.0

    producer_request_timeout_ms: int = 5000

    consumer_default_delay_ms: int = 500
    consumer_session_timeout_ms: int = 6000
    consumer_heartbeat_interval_ms: int = 1000
    consumer_fetch_timeout_ms: int = 200
    consumer_watermark_refresh_seconds: float = 1.0
    consumer_broker_call_timeout_seconds: float = 3.0
    consumer_commit_timeout_seconds: float = 5.0
    consumer_recent_messages: int = 50

    retry_initial_delays_seconds: tuple[float, ...] = (1, 2, 4, 8, 16)
    retry_max_delay_seconds: float = 30

    sse_heartbeat_seconds: float = 15
    log_level: str = "INFO"

    def broker_host(self, broker_id: int) -> str:
        return self.broker_host_pattern.format(broker_id=broker_id)

    @property
    def bootstrap_servers(self) -> list[str]:
        return [f"{self.broker_host(broker_id)}:{self.broker_port}" for broker_id in self.broker_ids]
