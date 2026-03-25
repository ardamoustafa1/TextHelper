from elasticsearch import AsyncElasticsearch

from app.core.config import settings
from app.core.logs import logger


class SearchService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        self.es_client = None
        self.available = False

        # Try connecting to Elasticsearch using configured host
        try:
            self.es_client = AsyncElasticsearch(
                [settings.ELASTICSEARCH_HOST],
                request_timeout=1,
                max_retries=0,
            )
            # Availability will be checked lazily in check_connection
            self.available = False
        except Exception as e:
            logger.warning(f"[SEARCH] ES Init Error: {e}")

        self.initialized = True

    async def check_connection(self):
        if not self.es_client:
            self.available = False
            return
        try:
            if await self.es_client.ping():
                if not self.available:
                    logger.info("[SEARCH] Elasticsearch connection successful.")
                self.available = True
            else:
                self.available = False
        except Exception:
            self.available = False


search_service = SearchService()
