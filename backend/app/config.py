from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    polygon_api_key: str | None = Field(default=None, env="POLYGON_API_KEY")
    alphavantage_api_key: str | None = Field(default=None, env="ALPHAVANTAGE_API_KEY")
    newsapi_key: str | None = Field(default=None, env="NEWSAPI_KEY")
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    database_url: str = Field(default="sqlite+aiosqlite:///./marketai.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://redis:6379/0", env="REDIS_URL")
    celery_broker_url: str = Field(default=None, env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default=None, env="CELERY_RESULT_BACKEND")
    model_dir: str = Field(default="/models", env="MODEL_DIR")
    signal_threshold: float = Field(default=0.75, env="SIGNAL_THRESHOLD")
    lookahead_hours: int = Field(default=6, env="LOOKAHEAD_HOURS")
    target_move_pct: float = Field(default=1.0, env="TARGET_MOVE_PCT")
    demo_mode: bool = Field(default=True, env="DEMO_MODE")
    class Config:
        env_file = ".env"

settings = Settings()
