import os
from typing import List


class Settings:
    """
    Central application configuration.
    All environment-driven behaviour should be defined here.
    """

    # Environment / runtime
    ENV: str = os.getenv("ENV", "dev").lower()  # dev / staging / prod
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Security
    API_KEY: str = os.getenv("API_KEY", "texthelper-secret-key-2024")
    # Comma-separated origins, e.g. "https://portal.vodafone.com,https://app.vodafone.com"
    ALLOWED_ORIGINS_RAW: str = os.getenv("ALLOWED_ORIGINS", "*")

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        if self.ALLOWED_ORIGINS_RAW.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS_RAW.split(",") if o.strip()]

    # Feature flags
    USE_TRANSFORMER: bool = os.getenv("USE_TRANSFORMER", "false").lower() == "true"
    USE_ELASTICSEARCH: bool = os.getenv("USE_ELASTICSEARCH", "false").lower() == "true"
    ENABLE_HEAVY_FEATURES: bool = os.getenv("ENABLE_HEAVY_FEATURES", "false").lower() == "true"

    # External services
    ELASTICSEARCH_HOST: str = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")


settings = Settings()
