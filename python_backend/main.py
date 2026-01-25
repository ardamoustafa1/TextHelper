"""
TextHelper ULTIMATE - Hybrid: Transformer + Elasticsearch + FastAPI
En iyi çözüm - Production ready
"""

from fastapi import FastAPI, WebSocket, HTTPException, Request, APIRouter
from starlette.websockets import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import asyncio
from datetime import datetime
import json
import os
import sys
from contextlib import asynccontextmanager
from fastapi.responses import ORJSONResponse

# Gzip Middleware (Optional)
try:
    from starlette.middleware.gzip import GZipMiddleware
except ImportError:
    try:
        from fastapi.middleware.gzip import GZipMiddleware
    except ImportError:
        GZipMiddleware = None

# Logger Import
from logger_config import logger

# Improvements modüllerini ekle
sys.path.append(os.path.join(os.path.dirname(__file__), 'improvements'))
try:
    from redis_cache import cache
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    cache = None


try:
    from large_dictionary import large_dictionary
    LARGE_DICT_AVAILABLE = True
except ImportError:
    LARGE_DICT_AVAILABLE = False
    large_dictionary = None

# YENI: Medium Dictionary (Reliable Fallback)
try:
    from medium_dictionary import medium_dictionary
    MEDIUM_DICT_AVAILABLE = True
except ImportError:
    MEDIUM_DICT_AVAILABLE = False
    medium_dictionary = None

try:
    from ml_learning import ml_learning
    ML_LEARNING_AVAILABLE = True
except ImportError:
    ML_LEARNING_AVAILABLE = False
    ml_learning = None

try:
    from transformer_model import transformer_model
    REAL_TRANSFORMER_AVAILABLE = True
except ImportError:
    REAL_TRANSFORMER_AVAILABLE = False
    transformer_model = None

try:
    from elasticsearch_setup import es_manager
    ES_MANAGER_AVAILABLE = True
except ImportError:
    ES_MANAGER_AVAILABLE = False
    es_manager = None

try:
    from advanced_ngram import advanced_ngram
    ADVANCED_NGRAM_AVAILABLE = True
except ImportError:
    ADVANCED_NGRAM_AVAILABLE = False
    advanced_ngram = None

# Eski context analyzer yerine gelişmiş olana öncelik veriyoruz
try:
    from context_analyzer import context_analyzer
    CONTEXT_ANALYZER_AVAILABLE = True
except ImportError:
    CONTEXT_ANALYZER_AVAILABLE = False
    context_analyzer = None

try:
    from advanced_context_completion import advanced_context_completer
    ADVANCED_CONTEXT_AVAILABLE = True
except ImportError:
    ADVANCED_CONTEXT_AVAILABLE = False
    advanced_context_completer = None

try:
    from advanced_ranking import advanced_ranking
    ADVANCED_RANKING_AVAILABLE = True
except ImportError:
    ADVANCED_RANKING_AVAILABLE = False
    advanced_ranking = None

try:
    from advanced_fuzzy import advanced_fuzzy
    ADVANCED_FUZZY_AVAILABLE = True
except ImportError:
    ADVANCED_FUZZY_AVAILABLE = False
    advanced_fuzzy = None

try:
    from phrase_completion import PhraseCompleter
    # Dictionary referansını geç (son kelime için genel arama için)
    if LARGE_DICT_AVAILABLE and large_dictionary:
        phrase_completer = PhraseCompleter(dictionary=large_dictionary)
    else:
        phrase_completer = PhraseCompleter()
    PHRASE_COMPLETION_AVAILABLE = True
except ImportError:
    PHRASE_COMPLETION_AVAILABLE = False
    phrase_completer = None

try:
    from domain_dictionaries import domain_manager
    DOMAIN_DICT_AVAILABLE = True
except ImportError:
    DOMAIN_DICT_AVAILABLE = False
    domain_manager = None

try:
    from security import security_manager
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    security_manager = None

try:
    from performance_optimizer import performance_optimizer
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False
    performance_optimizer = None

try:
    from emoji_suggestions import emoji_suggester
    EMOJI_AVAILABLE = True
except ImportError:
    EMOJI_AVAILABLE = False
    emoji_suggester = None

try:
    from smart_templates import smart_template_manager
    SMART_TEMPLATES_AVAILABLE = True
except ImportError:
    SMART_TEMPLATES_AVAILABLE = False
    smart_template_manager = None

try:
    from sentiment_analyzer import sentiment_analyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    sentiment_analyzer = None

# YENİ: Advanced Context Completion
try:
    from advanced_context_completion import AdvancedContextCompleter
    if LARGE_DICT_AVAILABLE and large_dictionary:
        advanced_context_completer = AdvancedContextCompleter(dictionary=large_dictionary)
    else:
        advanced_context_completer = AdvancedContextCompleter()
    ADVANCED_CONTEXT_AVAILABLE = True
except ImportError:
    ADVANCED_CONTEXT_AVAILABLE = False
    advanced_context_completer = None

# YENİ: ML Ranking
try:
    from ml_ranking import ml_ranking
    ML_RANKING_AVAILABLE = True
except ImportError:
    ML_RANKING_AVAILABLE = False
    ml_ranking = None

# YENİ: Trie Index
try:
    from trie_index import trie_index, TrieIndex
    TRIE_AVAILABLE = True
except ImportError:
    TRIE_AVAILABLE = False
    trie_index = None
    TrieIndex = None

# YENİ: Relevance Filter
try:
    from relevance_filter import relevance_filter
    RELEVANCE_FILTER_AVAILABLE = True
except ImportError:
    RELEVANCE_FILTER_AVAILABLE = False
    relevance_filter = None

# WhatsApp/iPhone benzeri: 1-2 karakter için öncelikli öneriler (merhaba, nasıl, ...)
try:
    from smart_completions import get_smart_completions
    SMART_COMPLETIONS_AVAILABLE = True
except ImportError:
    SMART_COMPLETIONS_AVAILABLE = False
    get_smart_completions = None

# iPhone benzeri: yaygın kelime önceliklendirmesi (hangi, merhaba, nasıl vb.)
try:
    from common_words import is_common, first_word_common
    COMMON_WORDS_AVAILABLE = True
except ImportError:
    COMMON_WORDS_AVAILABLE = False
    is_common = lambda w: False
    first_word_common = lambda t: False

# ============================================
# LIFESPAN (STARTUP/SHUTDOWN)
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    """Uygulama başlatıldığında"""
    logger.info("=" * 60)
    logger.info("TextHelper ULTIMATE - Hybrid System")
    logger.info("Transformer + Elasticsearch + FastAPI")
    logger.info("=" * 60)
    
    # Transformer modelini yükle - LAZY: Sadece USE_TRANSFORMER=true ise
    # Transformer çok ağır (CPU/GPU), varsayılan olarak kapalı
    use_transformer = os.getenv("USE_TRANSFORMER", "false").lower() == "true"
    if use_transformer and REAL_TRANSFORMER_AVAILABLE and transformer_model:
        try:
            logger.info("Transformer modeli yukleniyor (USE_TRANSFORMER=true)...")
            logger.info("NOT: Transformer CPU/GPU kullanimini artirir - sadece gerektiginde aktif edin")
            await transformer_model.load_model(timeout_seconds=30)  # 30s timeout (daha hızlı)
            if transformer_model.model_loaded:
                logger.info("RealTransformerModel yuklendi ve aktif!")
            else:
                logger.info("Transformer yuklenemedi, diger yontemler kullanilacak")
            
            # Sonra TransformerPredictor'ı yükle (sadece transformer aktifse)
            if transformer_model.model_loaded:
                await transformer_predictor.load_model()
        except Exception as e:
            logger.warning(f"Transformer yukleme hatasi: {e}")
            logger.info("Transformer olmadan devam ediliyor...")
    else:
        logger.info("Transformer devre disi (USE_TRANSFORMER=false) - CPU/GPU kullanimini azaltir")
        logger.info("Transformer'i aktif etmek icin: TUM_OZELLIKLERLE_BASLAT.bat kullanin")
    
    # Elasticsearch'e bağlan (opsiyonel - normal durum)
    try:
        await elasticsearch_predictor.connect_elasticsearch()
        
        if elasticsearch_predictor.es_client:
            logger.info("Elasticsearch baglantisi basarili!")
        else:
            # Normal durum - yerel sözlük kullanılacak (Elasticsearch opsiyonel)
            logger.info("Elasticsearch kullanilamiyor, yerel sozluk kullanilacak (normal)")
    except Exception as e:
        # Normal durum - yerel sözlük kullanılacak (Elasticsearch opsiyonel)
        logger.info("Elasticsearch kullanilamiyor, yerel sozluk kullanilacak (normal)")
    
    # ES Manager varsa kelimeleri index'le
    if ES_MANAGER_AVAILABLE and es_manager and hasattr(es_manager, 'available') and es_manager.available:
        # İlk başlatmada kelimeleri index'le (opsiyonel)
        logger.info("Elasticsearch Manager aktif - kelimeleri index'lemek icin /index_words endpoint'ini kullanin")
    
    # YENİ: Trie Index oluştur (performans için)
    if TRIE_AVAILABLE and TrieIndex and LARGE_DICT_AVAILABLE and large_dictionary:
        try:
            logger.info("Trie index oluşturuluyor (ultra hızlı arama için)...")
            trie_index.build_from_words(
                large_dictionary.words,
                large_dictionary.word_frequencies
            )
            stats = trie_index.get_stats()
            logger.info(f"Trie index hazır: {stats.get('word_count', 0):,} kelime, {stats.get('node_count', 0):,} node")
        except Exception as e:
            logger.warning(f"Trie index oluşturma hatası: {e}")
    
    # N-gram modeli istatistikleri
    if ADVANCED_NGRAM_AVAILABLE and advanced_ngram and hasattr(advanced_ngram, 'get_stats'):
        try:
            stats = advanced_ngram.get_stats()
            if stats and isinstance(stats, dict):
                logger.info(f"N-gram Modeli: {stats.get('bigrams', 0)} bigram, {stats.get('trigrams', 0)} trigram, {stats.get('quadgrams', 0)} quadgram")
        except Exception as e:
            logger.warning(f"N-gram stats hatasi: {e}")
    
    # Production mode kontrolü
    is_production = os.getenv("USE_TRANSFORMER", "false").lower() == "true" and os.getenv("ENABLE_HEAVY_FEATURES", "false").lower() == "true"
    
    logger.info("=" * 70)
    if is_production:
        logger.info("🚀 PRODUCTION MODE - MUSTERI HIZMETLERI ICIN HAZIR!")
        logger.info("=" * 70)
        logger.info("[PRODUCTION] Tum ozellikler aktif")
        logger.info("[PRODUCTION] 1M+ kelime hedefi")
        logger.info("[PRODUCTION] Vodafone, Turkcell, vb. entegrasyon icin hazir")
    else:
        logger.info("✅ SISTEM HAZIR (Minimal Mode)")
        logger.info("=" * 70)
        logger.info("Production mode icin: PRODUCTION_BASLAT.bat kullanin")
    logger.info("=" * 70)
    logger.info("[OK] Sistem hazir!")
    logger.info("API Docs: http://localhost:8000/docs")
    logger.info("WebSocket: ws://localhost:8000/ws")
    logger.info("Health: http://localhost:8000/health")
    logger.info(f"REDIS_PORT: {os.getenv('REDIS_PORT', '6379')}")
    logger.info("YENI OZELLIKLER:")
    
    if ADVANCED_NGRAM_AVAILABLE and advanced_ngram and hasattr(advanced_ngram, 'get_stats'):
        try:
            stats = advanced_ngram.get_stats()
            if stats and isinstance(stats, dict):
                logger.info(f"  - N-gram Modeli: {stats.get('bigrams', 0)} bigram, {stats.get('trigrams', 0)} trigram")
        except Exception:
            pass
            
    if CONTEXT_ANALYZER_AVAILABLE:
        logger.info("  - Context Analyzer: AKTIF")
    if ADVANCED_RANKING_AVAILABLE:
        logger.info("  - Advanced Ranking: AKTIF")
    logger.info("  - Real-Time Learning: AKTIF")
    logger.info("=" * 60)
    
    yield
    
    # --- SHUTDOWN ---
    logger.info("🛑 Sistem kapatılıyor...")
    if elasticsearch_predictor.es_client:
        # Sync vs Async client kontrolü
        try:
            close_res = elasticsearch_predictor.es_client.close()
            # Eğer async çalışıyorsa await et (coroutine döner)
            if close_res is not None and hasattr(close_res, '__await__'):
                await close_res
        except Exception as e:
            logger.warning(f"ES close warning: {e}")
            
    logger.info("✅ Kapanış tamamlandı")

# ============================================
# KONFIGÜRASYON
# ============================================

app = FastAPI(
    title="TextHelper ULTIMATE API",
    version="2.1.0",
    description="Hybrid: Transformer AI + Elasticsearch + FastAPI - En iyi otomatik tamamlama sistemi",
    lifespan=lifespan,
    default_response_class=ORJSONResponse
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if GZipMiddleware:
    app.add_middleware(GZipMiddleware, minimum_size=1000)

# API Key Middleware
API_KEY = os.getenv("API_KEY", "texthelper-secret-key-2024")

async def api_key_middleware(request: Request, call_next):
    # Health check ve docs hariç kontrol et
    if request.url.path in ["/docs", "/openapi.json", "/api/v1/health", "/health"]:
        return await call_next(request)
        
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        return ORJSONResponse(
            status_code=403,
            content={"code": "FORBIDDEN", "message": "Invalid or missing API Key"}
        )
    return await call_next(request)

app.add_middleware(BaseHTTPMiddleware, dispatch=api_key_middleware)

from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return ORJSONResponse(
        status_code=500,
        content=StandardErrorResponse(
            code="INTERNAL_SERVER_ERROR",
            message="Beklenmeyen sunucu hatasi",
            details={"error": str(exc)}
        ).model_dump()
    )

from typing import List, Optional, Dict, Generic, TypeVar

# ============================================
# MODELLER
# ============================================

class StandardErrorResponse(BaseModel):
    """Standart Hata Yanıtı Modeli"""
    code: str
    message: str
    details: Optional[Dict] = None
    timestamp: datetime = datetime.now()

class PredictionRequest(BaseModel):
    text: str
    context_message: Optional[str] = None  # YENİ: Önceki mesaj
    max_suggestions: Optional[int] = 80
    use_ai: Optional[bool] = True
    use_search: Optional[bool] = True
    user_id: Optional[str] = "default"

class Suggestion(BaseModel):
    text: str
    type: str
    score: float
    description: str
    source: str

class PredictionResponse(BaseModel):
    suggestions: List[Suggestion]
    corrected_text: Optional[str] = None
    processing_time_ms: float
    sources_used: List[str]

class FeedbackRequest(BaseModel):
    text: str
    selected_suggestion: str
    user_id: str = "default"

# ============================================
# 1. TRANSFORMER MODEL (AI TAHMİNLERİ)
# ============================================

class TransformerPredictor:
    """AI tabanlı tahminler için Transformer modeli"""
    
    def __init__(self):
        self.model_loaded = False
        self.model = None
        self.tokenizer = None
        self.use_transformer = os.getenv("USE_TRANSFORMER", "false").lower() == "true"
        
    async def load_model(self):
        """Transformer modelini yükle"""
        # ÖNCE: Gerçek transformer modeli kullan (varsa) - HER ZAMAN DENE!
        if REAL_TRANSFORMER_AVAILABLE and transformer_model:
            await transformer_model.load_model()
            self.model_loaded = transformer_model.model_loaded
            if self.model_loaded:
                print("[OK] Gercek Transformer modeli yuklendi")
                return
        
        # Fallback: Pattern-based (sadece gerçek model yoksa)
        if not self.use_transformer and not self.model_loaded:
            print("[INFO] Transformer kullanimi devre disi (USE_TRANSFORMER=true ile aktif edin)")
            print("[INFO] Gercek Transformer modeli yuklenemedi, pattern-based fallback kullanilacak")
            return
            
        try:
            # Hugging Face transformers
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            print("[INFO] Transformer modeli yukleniyor...")
            # BERT yerine GPT-2 modeline geçiş (Text Generation için daha uygun)
            model_name = "ytu-ce-cosmos/turkish-gpt2-medium"
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.model.eval()  # Evaluation mode
            
            self.model_loaded = True
            print("[OK] Transformer modeli hazir")
        except ImportError:
            print("[WARNING] transformers kutuphanesi kurulu degil: pip install transformers torch")
            self.model_loaded = False
        except Exception as e:
            print(f"[WARNING] Transformer modeli yuklenemedi: {e}")
            self.model_loaded = False
    
    async def predict(self, text: str, max_suggestions: int = 5) -> List[Suggestion]:
        """AI ile tahmin yap"""
        # Gerçek transformer modeli kullan (varsa)
        if REAL_TRANSFORMER_AVAILABLE and transformer_model and transformer_model.model_loaded:
            results = await transformer_model.predict(text, max_suggestions)
            return [Suggestion(**r) for r in results]
        
        if not self.model_loaded:
            return self._fallback_predictions(text, max_suggestions)
        
        try:
            import torch
            # Gerçek transformer tahmini
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=inputs['input_ids'].shape[1] + 20,
                    num_return_sequences=max_suggestions,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            suggestions = []
            for output in outputs:
                generated_text = self.tokenizer.decode(output, skip_special_tokens=True)
                # Son kelimeyi al
                last_word = generated_text.split()[-1] if generated_text.split() else ""
                
                if last_word and last_word not in [s.text for s in suggestions]:
                    suggestions.append(Suggestion(
                        text=last_word,
                        type="ai_prediction",
                        score=9.5,
                        description="AI tahmini (Transformer)",
                        source="transformer"
                    ))
            
            return suggestions[:max_suggestions]
        except Exception as e:
            print(f"Transformer tahmin hatası: {e}")
            return self._fallback_predictions(text, max_suggestions)
    
    def _fallback_predictions(self, text: str, max_suggestions: int) -> List[Suggestion]:
        """Fallback: Akıllı pattern matching"""
        suggestions = []
        words = text.split()
        last_word = words[-1].lower() if words else text.lower()
        
        # Türkçe pattern'ler
        patterns = {
            'man': ['mantık', 'mantıklı', 'mantıksız', 'mantıken', 'mantıksal'],
            'nas': ['nasıl', 'nasıl yardımcı', 'nasıl olabilirim', 'nasıl yapabilirim'],
            'mer': ['merhaba', 'merhaba size', 'merhaba nasıl', 'merhaba hoş'],
            'teş': ['teşekkür', 'teşekkürler', 'teşekkür ederim', 'teşekkür ederiz'],
            'yar': ['yardım', 'yardımcı', 'yardımcı olabilirim', 'yardım etmek'],
            'müs': ['müşteri', 'müşteri hizmetleri', 'müşteri desteği', 'müşteri memnuniyeti'],
            'sip': ['sipariş', 'siparişiniz', 'sipariş takibi', 'sipariş durumu'],
            'ara': ['ara', 'araba', 'arama', 'aramak', 'arayabilirsiniz'],
            'aç': ['açık', 'açmak', 'açıklama', 'açıklamak', 'açıklayabilirim'],
        }
        
        prefix = last_word[:3] if len(last_word) >= 3 else last_word
        if prefix in patterns:
            for word in patterns[prefix][:max_suggestions]:
                suggestions.append(Suggestion(
                    text=word,
                    type="ai_prediction",
                    score=9.0,
                    description="AI tahmini (Pattern)",
                    source="transformer"
                ))
        
        return suggestions

transformer_predictor = TransformerPredictor()

# ============================================
# 2. ELASTICSEARCH (HIZLI SÖZLÜK ARAMA)
# ============================================

class ElasticsearchPredictor:
    """Elasticsearch ile hızlı sözlük arama"""
    
    def __init__(self):
        self.es_client = None
        self.use_elasticsearch = os.getenv("USE_ELASTICSEARCH", "false").lower() == "true"
        self.local_dictionary = [] # Lazy load
        self._dictionary_loaded = False
        
    def _load_dictionary(self) -> List[str]:
        """Yerel sözlük yükle (Elasticsearch yoksa)"""
        if self._dictionary_loaded:
            return self.local_dictionary
            
        # Büyük Türkçe sözlük
        dictionary_file = os.path.join(os.path.dirname(__file__), "turkish_dictionary.txt")
        
        try:
            if os.path.exists(dictionary_file):
                print(f"[INFO] Sözlük yükleniyor... ({dictionary_file})")
                with open(dictionary_file, 'r', encoding='utf-8') as f:
                    # Generator kullanarak belleği koru (ama liste lazım ise mecburen)
                    # Sadece ilk 500k kelimeyi alalim memory korumak icin
                    lines = []
                    count = 0
                    for line in f:
                        if line.strip():
                            lines.append(line.strip())
                            count += 1
                            if count >= 500000: # Limit memory usage
                                break
                    
                self._dictionary_loaded = True
                print(f"[OK] Sözlük yüklendi ({len(lines)} kelime)")
                return lines
        except MemoryError:
            print("[WARNING] Yetersiz bellek - Büyük sözlük yüklenemedi. Varsayılan küçük sözlük kullanılacak.")
        except Exception as e:
            print(f"[WARNING] Sözlük yükleme hatası: {e}")
        
        # Varsayılan sözlük (Fallback)
        self._dictionary_loaded = True
        return [
            # Mantık kelimeleri
            'mantık', 'mantıklı', 'mantıksız', 'mantıken', 'mantıksal', 'mantıkça',
            # Merhaba ve selamlaşma
            'merhaba', 'merhaba size', 'merhaba nasıl', 'merhaba hoş', 'selam',
            'selamlar', 'selamun aleyküm', 'hoş geldiniz', 'hoş geldin',
            # Teşekkür
            'teşekkür', 'teşekkürler', 'teşekkür ederim', 'teşekkür ederiz',
            'teşekkür ediyorum', 'teşekkür ediyoruz', 'sağolun', 'sağ olun',
            # Yardım
            'yardım', 'yardımcı', 'yardımcı olabilirim', 'yardım etmek',
            'yardımcı olmak', 'destek', 'destek olmak', 'destek vermek',
            # Müşteri
            'müşteri', 'müşteri hizmetleri', 'müşteri desteği', 'müşteri memnuniyeti',
            'müşteri temsilcisi', 'müşteri danışmanı',
            # Sipariş
            'sipariş', 'siparişiniz', 'sipariş takibi', 'sipariş durumu',
            'sipariş vermek', 'sipariş almak',
            # Ara
            'ara', 'araba', 'arama', 'aramak', 'arayabilirsiniz', 'arayabilirim',
            'arama yapmak', 'arama sonuçları',
            # Aç
            'açık', 'açmak', 'açıklama', 'açıklamak', 'açıklayabilirim',
            'açıklayabilir misiniz', 'açıklayabilir misin',
            # Nasıl
            'nasıl', 'nasıl yardımcı', 'nasıl olabilirim', 'nasıl yapabilirim',
            'nasıl yapılır', 'nasıl kullanılır',
            # Diğer yaygın kelimeler
            'iyi', 'kötü', 'güzel', 'büyük', 'küçük', 'yeni', 'eski',
            'yapmak', 'etmek', 'olmak', 'gelmek', 'gitmek', 'vermek', 'almak',
            'sorun', 'problem', 'çözüm', 'bilgi', 'detay', 'fiyat', 'ücret',
            'ürün', 'hizmet', 'kargo', 'teslimat', 'iade', 'değişim',
        ]
    
    async def connect_elasticsearch(self):
        """Elasticsearch'e bağlan"""
        # ES Manager kullan (varsa)
        if ES_MANAGER_AVAILABLE and es_manager:
            try:
                if hasattr(es_manager, 'connect'):
                    await es_manager.connect()
                if hasattr(es_manager, 'available') and es_manager.available:
                    if hasattr(es_manager, 'es_client'):
                        self.es_client = es_manager.es_client
                    print("[OK] Elasticsearch Manager ile baglanti kuruldu")
                    return
            except Exception as e:
                print(f"[WARNING] ES manager connect hatasi: {e}")
        
        # Fallback: Direkt bağlantı (USE_ELASTICSEARCH kontrolü kaldırıldı - her zaman dene)
        try:
            from elasticsearch import Elasticsearch
            
            es_host = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
            # URL formatını düzelt (http:// ekle)
            if not es_host.startswith("http://") and not es_host.startswith("https://"):
                es_host = f"http://{es_host}"
            
            # Elasticsearch client oluştur (timeout ve retry ile)
            self.es_client = Elasticsearch(
                [es_host],
                request_timeout=10,
                max_retries=2,
                retry_on_timeout=True
            )
            
            # Bağlantı testi (ping)
            try:
                if self.es_client.ping():
                    print(f"[OK] Elasticsearch baglantisi kuruldu: {es_host}")
                else:
                    print("[WARNING] Elasticsearch'e baglanilamadi (ping basarisiz), yerel sozluk kullanilacak")
                    print("[INFO] Elasticsearch calisiyor mu kontrol edin: http://localhost:9200")
                    print("[INFO] Elasticsearch baslatmak icin: DOCKER_BASLAT.bat")
                    self.es_client = None
            except Exception as ping_error:
                # Normal durum - yerel sözlük kullanılacak (Elasticsearch opsiyonel)
                print(f"[INFO] Elasticsearch kullanilamiyor, yerel sozluk kullanilacak (normal)")
                print(f"[INFO] Elasticsearch'i aktif etmek icin: DOCKER_BASLAT.bat")
                self.es_client = None
        except ImportError:
            print("[WARNING] elasticsearch kutuphanesi kurulu degil: pip install elasticsearch")
            self.es_client = None
        except Exception as e:
            error_msg = str(e)
            # Normal durum - yerel sözlük kullanılacak (Elasticsearch opsiyonel)
            print(f"[INFO] Elasticsearch kullanilamiyor, yerel sozluk kullanilacak (normal)")
            print(f"[INFO] Elasticsearch'i aktif etmek icin: DOCKER_BASLAT.bat")
            self.es_client = None
    
    async def search(self, prefix: str, max_results: int = 50) -> List[Suggestion]:  # Artırıldı: 10 -> 50
        """Elasticsearch'te ara (veya yerel sözlükte)"""
        if self.es_client:
            return await self._elasticsearch_search(prefix, max_results)
        else:
            return await self._local_search(prefix, max_results)
    
    async def _elasticsearch_search(self, prefix: str, max_results: int) -> List[Suggestion]:
        """Elasticsearch ile ara"""
        # ES Manager kullan (varsa)
        if ES_MANAGER_AVAILABLE and es_manager and hasattr(es_manager, 'available') and es_manager.available:
            try:
                if hasattr(es_manager, 'search'):
                    results = await es_manager.search(prefix, max_results)
                    if results and isinstance(results, list):
                        return [Suggestion(**r) for r in results if isinstance(r, dict)]
            except Exception as e:
                print(f"[WARNING] ES manager search hatasi: {e}")
        
        # Fallback: Direkt ES query
        if not self.es_client:
            return await self._local_search(prefix, max_results)
        
        try:
            query = {
                "suggest": {
                    "word-suggest": {
                        "prefix": prefix.lower(),
                        "completion": {
                            "field": "word_suggest",
                            "size": max_results
                        }
                    }
                }
            }
            
            response = self.es_client.search(index="turkish_words", body=query)
            suggestions = []
            
            for option in response.get('suggest', {}).get('word-suggest', [{}])[0].get('options', []):
                suggestions.append(Suggestion(
                    text=option['text'],
                    type="dictionary",
                    score=8.0 + (option.get('score', 0) / 100),
                    description="Sözlük (Elasticsearch)",
                    source="elasticsearch"
                ))
            
            return suggestions
        except Exception as e:
            print(f"Elasticsearch arama hatası: {e}")
            return await self._local_search(prefix, max_results)
    
    async def _local_search(self, prefix: str, max_results: int) -> List[Suggestion]:
        """Yerel sözlükte ara - WHATSAPP BENZERİ (her karakter için anlık öneri)"""
        suggestions = []
        prefix_lower = prefix.lower().strip()
        
        # Boş prefix kontrolü
        if not prefix_lower:
            return suggestions
            
        # Lazy load check
        if not self.local_dictionary and not self._dictionary_loaded:
             self.local_dictionary = self._load_dictionary()
        
        # WHATSAPP BENZERİ: Büyük sözlük kullan (varsa) - ÖNCELİK!
        if LARGE_DICT_AVAILABLE and large_dictionary:
            try:
                results = large_dictionary.search(prefix_lower, max_results)
                if results:
                    for result in results:
                        suggestions.append(Suggestion(
                            text=result['word'],
                            type="dictionary",
                            score=result.get('score', 8.0),
                            description=f"Sözlük (frekans: {result.get('frequency', 0)})",
                            source="large_dictionary"
                        ))
                    return suggestions
            except Exception as e:
                print(f"Large dictionary search hatası: {e}")
                # Fallback'e geç
        
        # WHATSAPP BENZERİ: Varsayılan sözlük (fallback - hızlı)
        for word in self.local_dictionary:
            word_lower = word.lower()
            
            # WHATSAPP BENZERİ: Prefix match - her karakter için öneri
            if len(prefix_lower) >= 1 and word_lower.startswith(prefix_lower) and word_lower != prefix_lower:
                # WHATSAPP BENZERİ: Skorlama - prefix uzunluğu önemli
                if len(prefix_lower) == 1:
                    score = 9.5 - (len(word_lower) * 0.02)  # Kısa kelimeler öncelikli
                elif len(prefix_lower) == 2:
                    score = 9.0 - (len(word_lower) * 0.01)  # İki harf
                else:
                    score = (len(prefix_lower) / len(word_lower)) * 8.5  # Çok harf
                
                suggestions.append(Suggestion(
                    text=word,
                    type="dictionary",
                    score=score,
                    description="Sözlük",
                    source="local_dictionary"
                ))
                
                # WHATSAPP BENZERİ: Yeterli öneri bulunduysa dur (hızlı yanıt)
                if len(suggestions) >= max_results * 2:
                    break
        
        # WHATSAPP BENZERİ: Skora göre sırala (en yüksek skorlu öneriler önce)
        suggestions.sort(key=lambda x: x.score, reverse=True)
        return suggestions[:max_results]

elasticsearch_predictor = ElasticsearchPredictor()

# ============================================
# 3. YAZIM DÜZELTME
# ============================================

class SpellChecker:
    """Yazım düzeltme - Lazy loading ile bellek hatası önleme"""
    
    def __init__(self):
        self.speller = None
        self.available = False
        self._initialized = False
    
    def _initialize(self):
        """Lazy initialization - sadece gerektiğinde yükle"""
        if self._initialized:
            return
        
        self._initialized = True
        
        try:
            from autocorrect import Speller
            # Türkçe model yüklemeyi dene
            try:
                self.speller = Speller(lang='tr')
                self.available = True
                print("[OK] Yazim duzeltme aktif (autocorrect)")
            except MemoryError:
                print("[WARNING] autocorrect bellek hatasi - yazim duzeltme devre disi")
                self.available = False
            except Exception as e:
                print(f"[WARNING] autocorrect yukleme hatasi: {e}")
                self.available = False
        except ImportError:
            self.available = False
            print("[WARNING] autocorrect kurulu degil: pip install autocorrect")
    
    async def check(self, word: str) -> Optional[str]:
        """Yazım hatasını düzelt"""
        # Lazy initialization
        if not self._initialized:
            self._initialize()
        
        if not self.available or not self.speller or len(word) <= 3:
            return None
        
        try:
            corrected = self.speller(word)
            return corrected if corrected != word else None
        except MemoryError:
            # Bellek hatası durumunda devre dışı bırak
            self.available = False
            return None
        except Exception:
            return None

spell_checker = SpellChecker()

# ============================================
# 4. HYBRID ORCHESTRATOR (BİRLEŞTİRME)
# ============================================

class HybridOrchestrator:
    """Transformer ve Elasticsearch sonuçlarını birleştir"""
    
    # Backend-side debouncing (50ms cooldown per user)
    _last_request = {}
    _DEBOUNCE_MS = 50  # 50ms
    
    # LRU Cache for search results (max 500 entries)
    from functools import lru_cache
    
    @staticmethod
    @lru_cache(maxsize=500)
    def _cached_search(prefix: str, max_results: int) -> tuple:
        """Cached search results (returns tuple for hashability)"""
        if LARGE_DICT_AVAILABLE and large_dictionary:
            results = large_dictionary.search(prefix, max_results)
            return tuple(results) if results else ()
        return ()
    
    async def predict(
        self,
        text: str,
        context_message: str = None,  # YENİ
        max_suggestions: int = 50,
        use_ai: bool = True,
        use_search: bool = True,
        user_id: str = "default"
    ) -> PredictionResponse:
        """Hybrid tahmin yap"""
        import time
        
        # Backend Debouncing: Skip if request too fast (CPU optimization)
        now = time.time() * 1000
        last = self._last_request.get(user_id, 0)
        if now - last < self._DEBOUNCE_MS:
            # Return empty response for too-fast requests
            return PredictionResponse(
                suggestions=[],
                processing_time_ms=0,
                sources_used=["debounced"]
            )
        self._last_request[user_id] = now
        
        start_time = datetime.now()
        sources_used = []
        all_suggestions = []
        
        # 0. CONTEXTUAL REPLIES (En Üst Öncelik - Eğer input boşsa veya kısaysa)
        if context_message and (not text or len(text) < 3):
            # Basit kural tabanlı Replies (İleride AI kullanılabilir)
            replies = []
            cm_lower = context_message.lower()
            
            if "nasılsın" in cm_lower or "naber" in cm_lower:
                replies = ["İyiyim, teşekkürler", "Teşekkürler, siz nasılsınız?", "Her şey yolunda"]
            elif "yardım" in cm_lower:
                replies = ["Nasıl yardımcı olabilirim?", "Sorun nedir?", "Buyurun, dinliyorum"]
            elif "sipariş" in cm_lower:
                replies = ["Sipariş numaranız nedir?", "Hemen kontrol ediyorum"]
            elif "merhaba" in cm_lower or "selam" in cm_lower:
                replies = ["Merhabalar", "Selamlar", "Hoş geldiniz"]
                
            if replies:
                for reply in replies:
                    all_suggestions.append(Suggestion(
                        text=reply,
                        type="smart_reply",
                        score=50.0, # Çok yüksek skor
                        description="Akıllı Yanıt",
                        source="contextual_reply"
                    ))
                
                # Eğer yanıt bulduysak ve text boşsa, direkt dön
                if not text and all_suggestions:
                     end_time = datetime.now()
                     processing_time = (end_time - start_time).total_seconds() * 1000
                     return PredictionResponse(
                        suggestions=all_suggestions,
                        processing_time_ms=processing_time,
                        sources_used=["contextual_reply"]
                    )
        
        # WHATSAPP BENZERİ: Cache tamamen devre dışı - her karakter için yeni öneri!
        # WhatsApp iPhone gibi çalışması için cache kullanma
        cache_key = None
        # Cache devre dışı - her karakter için anlık öneri
        # if REDIS_AVAILABLE and cache:
        #     try:
        #         cache_key = cache.generate_key("predict", text, max_suggestions, use_ai, use_search)
        #         cached_result = cache.get(cache_key)
        #         if cached_result:
        #             return PredictionResponse(**cached_result)
        #     except Exception as e:
        #         print(f"[WARNING] Cache kontrol hatasi: {e}")
        
        # HYBRID: Context analizi (ARKA PLANDA - hızlı önerilerden sonra)
        # WhatsApp/iPhone: Önce hızlı öneriler, sonra context-aware öneriler
        context = None
        # if CONTEXT_ANALYZER_AVAILABLE and context_analyzer:
        #     # Context analizi hafif, ekle (arka planda çalışır)
        #     try:
        #         context = context_analyzer.analyze(text)
        #     except Exception:
        #         context = None
        
        # YENI: Gelişmiş Context Analizi (Öncelikli)
        if ADVANCED_CONTEXT_AVAILABLE and advanced_context_completer:
             try:
                 # Akıllı yanıtları ve context önerilerini ekle
                 smart_responses = advanced_context_completer.generate_smart_responses(text)
                 if smart_responses:
                     all_suggestions.extend(smart_responses)
                 
                 context_suggestions = advanced_context_completer.complete_with_full_context(text, max_suggestions)
                 if context_suggestions:
                     all_suggestions.extend(context_suggestions)
             except Exception as e:
                 print(f"[WARNING] Advanced Context hatasi: {e}")
        
        # YENI: ML Learning (Kişiselleştirilmiş Öneriler)
        if ML_LEARNING_AVAILABLE and ml_learning:
            try:
                # Kullanıcıya özel sıralama
                all_suggestions = ml_learning.get_personalized_suggestions(user_id, text, all_suggestions)
            except Exception as e:
                print(f"[WARNING] ML Learning hatasi: {e}")

        # Paralel olarak her kaynaktan al
        tasks = []
        
        # 1. HYBRID: AI Tahminleri (Transformer) - ARKA PLANDA (sadece heavy features aktifse)
        # WhatsApp/iPhone: Transformer kullanmaz ama biz hybrid yaklaşımla ekleyebiliriz
        # Önce hızlı öneriler gösterilir, sonra Transformer önerileri gelir (arka planda)
        use_transformer = os.getenv("USE_TRANSFORMER", "false").lower() == "true"
        enable_heavy_features = os.getenv("ENABLE_HEAVY_FEATURES", "false").lower() == "true"
        
        if use_ai and use_transformer and enable_heavy_features:
            # Transformer: Arka planda çalışır (smart_tasks'a eklenir - akıllı öneriler)
            tasks.append(self._get_ai_predictions(text, max_suggestions, sources_used))
        
        # 2. WHATSAPP BENZERİ: Sözlük Arama - Son kelimeye odaklan, her karakter için güncelle!
        # WhatsApp iPhone gibi: "a" -> "ak" -> "akı" -> "akıl" her adımda güncelleniyor
        if use_search:
            words = text.split()
            last_word = words[-1] if words else text
            last_word = last_word.strip()
            
            # ALKALI ÖNERİLER İÇİN: Her karakter için öneri ver (>= 1) - GARANTİLİ!
            if len(last_word) >= 1:
                # Öncelik: Trie Index (en hızlı - WhatsApp benzeri anlık öneri)
                if TRIE_AVAILABLE and trie_index and hasattr(trie_index, 'word_count') and trie_index.word_count > 0:
                    tasks.append(self._get_trie_predictions(last_word, max_suggestions * 6, sources_used))
                
                # Her zaman local search (fallback - GARANTİLİ!)
                tasks.append(self._get_search_predictions(last_word, max_suggestions * 6, sources_used))
                
                # KELİME SAYISINI ARTIRMAK İÇİN: Large dictionary'den direkt arama (tüm uzunluklar için)
                if LARGE_DICT_AVAILABLE and large_dictionary:
                    tasks.append(self._get_direct_large_dict_predictions(last_word, max_suggestions * 5, sources_used))
                
                # YENI: Medium Dictionary (Reliable & Fast Fallback)
                if MEDIUM_DICT_AVAILABLE and medium_dictionary:
                    # Senkron olduğu için direkt çalıştırabiliriz veya async wrapper yapabiliriz
                    # Hızlı olduğu için direkt ekleyelim
                    try:
                        md_results = medium_dictionary.search(last_word, max_suggestions)
                        if md_results:
                            md_suggestions = [Suggestion(
                                text=res['word'],
                                type='dictionary',
                                score=res['score'],
                                description='Sözlük (Medium)',
                                source='medium_dictionary'
                            ) for res in md_results]
                            all_suggestions.extend(md_suggestions)
                    except Exception as e:
                        print(f"[WARNING] Medium dictionary hatasi: {e}")
        
        # 3. N-Gram Tahminleri (Hafif - aktif)
        if ADVANCED_NGRAM_AVAILABLE and advanced_ngram:
            tasks.append(self._get_ngram_predictions(text, max_suggestions * 2, sources_used))
        
        # 4. Phrase Completion (Hafif - aktif)
        if PHRASE_COMPLETION_AVAILABLE and phrase_completer:
            tasks.append(self._get_phrase_predictions(text, max_suggestions * 2, sources_used))
        
        # 5. Domain-Specific (müşteri hizmeti odaklı - HER ZAMAN)
        if DOMAIN_DICT_AVAILABLE and domain_manager:
            tasks.append(self._get_domain_predictions(text, max_suggestions * 2, sources_used))
        
        enable_heavy_features = os.getenv("ENABLE_HEAVY_FEATURES", "false").lower() == "true"
        
        # 6. Emoji Suggestions (Hafif - aktif)
        if EMOJI_AVAILABLE and emoji_suggester:
            tasks.append(self._get_emoji_predictions(text, max_suggestions * 2, sources_used))
        
        # 7. Smart Templates (Ağır - opsiyonel)
        if enable_heavy_features and SMART_TEMPLATES_AVAILABLE and smart_template_manager:
            tasks.append(self._get_template_predictions(text, max_suggestions * 2, sources_used))
        
        # HYBRID YAKLAŞIM: İki aşamalı öneri sistemi
        # AŞAMA 1: Hızlı öneriler (Trie + Large Dict) - milisaniyelik yanıt
        # AŞAMA 2: Akıllı öneriler (N-gram, Phrase, Context) - arka planda
        
        # Hızlı task'lar (Trie, Large Dict) - önce çalıştır
        fast_tasks = []
        smart_tasks = []
        
        for task in tasks:
            # Task'ın kaynağını kontrol et (basit kontrol)
            task_str = str(task)
            if 'trie' in task_str.lower() or 'large_dict' in task_str.lower() or 'direct_large_dict' in task_str.lower():
                fast_tasks.append(task)
            else:
                smart_tasks.append(task)
        
        # AŞAMA 1: Hızlı öneriler (100ms timeout - milisaniyelik yanıt)
        async def with_fast_timeout(task):
            try:
                return await asyncio.wait_for(task, timeout=0.1)  # 100ms
            except (asyncio.TimeoutError, Exception):
                return []
        
        fast_results = []
        if fast_tasks:
            fast_results = await asyncio.gather(*[with_fast_timeout(task) for task in fast_tasks], return_exceptions=True)
        
        # AŞAMA 2: Akıllı öneriler (500ms timeout - arka planda, hızlı önerilerden sonra)
        async def with_smart_timeout(task):
            try:
                return await asyncio.wait_for(task, timeout=0.5)  # 500ms
            except (asyncio.TimeoutError, Exception):
                return []
        
        smart_results = []
        if smart_tasks:
            # Arka planda çalıştır (hızlı öneriler gösterildikten sonra)
            smart_results = await asyncio.gather(*[with_smart_timeout(task) for task in smart_tasks], return_exceptions=True)
        
        # Sonuçları birleştir (hızlı öneriler önce, akıllı öneriler sonra)
        results = fast_results + smart_results
        
        # Sonuçları birleştir
        for result in results:
            if isinstance(result, Exception):
                print(f"[WARNING] Task hatasi: {result}")
                continue
            if isinstance(result, list):
                all_suggestions.extend(result)
        
        # WhatsApp/iPhone benzeri: 1-2 karakter için öncelikli öneriler (m→merhaba, n→nasıl, ...)
        if SMART_COMPLETIONS_AVAILABLE and get_smart_completions and use_search and text:
            _words = text.split()
            _lw = (_words[-1] if _words else text).strip()
            if 1 <= len(_lw) <= 4:
                comps = get_smart_completions(_lw, max_suggestions * 3)
                for d in comps:
                    all_suggestions.insert(0, Suggestion(
                        text=d["word"],
                        type=d.get("type", "smart_completion"),
                        score=d.get("score", 14.0),
                        description=d.get("description", "Öneri (öncelikli)"),
                        source=d.get("source", "smart_completions")
                    ))
                if comps and "smart_completions" not in sources_used:
                    sources_used.append("smart_completions")
        
        # 4-9. HYBRID: Akıllı özellikler (ARKA PLANDA - hızlı önerilerden sonra)
        # WhatsApp/iPhone: Önce hızlı öneriler gösterilir, sonra daha akıllı öneriler gelir
        corrected_text = None
        
        # ALKALI ÖNERİLER: Context-aware filtreleme (HER ZAMAN AKTİF - alakalı öneriler için)
        if CONTEXT_ANALYZER_AVAILABLE and context_analyzer and context and all_suggestions:
            try:
                all_suggestions_dict = [{'text': s.text, 'score': s.score, 'type': s.type, 'source': s.source, 'description': s.description} for s in all_suggestions]
                filtered = context_analyzer.filter_suggestions_by_context(all_suggestions_dict, context)
                if filtered and isinstance(filtered, list) and len(filtered) > 0:
                    # ALKALI ÖNERİLER İÇİN: Context'e uygun önerileri önceliklendir ve skorla
                    context_suggestions = [Suggestion(**s) for s in filtered if isinstance(s, dict)]
                    # Context önerilerine bonus skor ver (alkalı öneriler için)
                    for ctx_sug in context_suggestions:
                        ctx_sug.score += 2.0  # Context bonus (alkalı öneriler için)
                    # Context önerilerini başa ekle (öncelikli)
                    all_suggestions = context_suggestions + [s for s in all_suggestions if s not in context_suggestions]
            except Exception as e:
                pass  # Hata olursa devam et
        
        # Fuzzy Matching (sadece uzun kelimeler için - hafif)
        enable_heavy_features = os.getenv("ENABLE_HEAVY_FEATURES", "false").lower() == "true"
        if text:
            words = text.split()
            if words:
                last_word = words[-1]
                # Sadece uzun kelimeler için fuzzy matching (hızlı)
                if len(last_word) > 4 and ADVANCED_FUZZY_AVAILABLE and advanced_fuzzy and LARGE_DICT_AVAILABLE and large_dictionary:
                    try:
                        candidates = large_dictionary.words[:200]  # Çok az aday (hızlı)
                        fuzzy_matches = advanced_fuzzy.match(last_word, candidates, max_results=1)
                        if fuzzy_matches and fuzzy_matches[0]['confidence'] > 0.8:
                            corrected = fuzzy_matches[0]['word']
                            corrected_text = ' '.join(words[:-1] + [corrected])
                    except Exception:
                        pass
        
        # Advanced Context Completion (hafif - arka planda)
        if ADVANCED_CONTEXT_AVAILABLE and advanced_context_completer and all_suggestions:
            try:
                # Timeout ile (çok hızlı)
                context_suggestions = await asyncio.wait_for(
                    asyncio.to_thread(advanced_context_completer.complete_with_full_context, text, max_suggestions),
                    timeout=0.3  # 300ms timeout
                )
                if context_suggestions:
                    for ctx_sug in context_suggestions[:5]:  # Sadece ilk 5 (hızlı)
                        if isinstance(ctx_sug, dict):
                            all_suggestions.append(Suggestion(
                                text=ctx_sug.get('text', ''),
                                type=ctx_sug.get('type', 'phrase'),
                                score=ctx_sug.get('score', 0.0),
                                description=ctx_sug.get('description', ''),
                                source=ctx_sug.get('source', 'advanced_context')
                            ))
            except (asyncio.TimeoutError, Exception):
                pass  # Timeout olursa devam et
        
        # 9.1. ALKALI ÖNERİLER: Relevance Filter (HER ZAMAN AKTİF - alakasız önerileri filtrele)
        # Yazılan ile alakalı öneriler için relevance filter her zaman aktif
        words = text.split()
        last_word = words[-1] if words else text
        
        # ALKALI ÖNERİLER İÇİN: Her zaman filtrele (sadece çok fazla öneri değil)
        # Minimum 2 karakter ve en az 5 öneri varsa filtrele
        should_filter = len(all_suggestions) > 5 and len(last_word) >= 2
        
        if RELEVANCE_FILTER_AVAILABLE and relevance_filter and all_suggestions and should_filter:
            try:
                suggestions_dict = [
                    {
                        'text': s.text,
                        'score': s.score,
                        'type': s.type,
                        'source': s.source,
                        'description': s.description,
                        'frequency': getattr(s, 'frequency', 1)
                    }
                    for s in all_suggestions
                ]
                # ALKALI ÖNERİLER İÇİN: Relevance filter (alkalasız önerileri filtrele)
                filtered = relevance_filter.filter_irrelevant(suggestions_dict, text, max_suggestions * 5)
                filtered = relevance_filter.remove_duplicates(filtered)
                
                if filtered and isinstance(filtered, list) and len(filtered) > 0:
                    all_suggestions = [Suggestion(**s) for s in filtered if isinstance(s, dict)]
            except Exception:
                pass  # Hata olursa devam et
        
        # 9.2. HYBRID: ML Ranking (ARKA PLANDA - sadece heavy features aktifse)
        # WhatsApp/iPhone: ML ranking kullanır ama arka planda
        enable_heavy_features = os.getenv("ENABLE_HEAVY_FEATURES", "false").lower() == "true"
        if enable_heavy_features and ML_RANKING_AVAILABLE and ml_ranking and all_suggestions:
            try:
                context_dict = {'text': text, 'domain': 'general'}
                suggestions_dict = [
                    {
                        'text': s.text,
                        'score': s.score,
                        'type': s.type,
                        'source': s.source,
                        'frequency': getattr(s, 'frequency', 1),
                        'context_match': True,
                        'domain_match': True,
                        'grammar_match': False,
                        'semantic_score': 0.5
                    }
                    for s in all_suggestions
                ]
                ranked = ml_ranking.rank_suggestions(suggestions_dict, context_dict, user_id)
                
                if ranked and isinstance(ranked, list):
                    all_suggestions = [Suggestion(**s) for s in ranked if isinstance(s, dict)]
            except Exception as e:
                print(f"[WARNING] ML ranking hatasi: {e}")
        
        # 9.3. Yazılan prefix'in kendisini öneri olarak gösterme ("mer" -> "mer" çıkmaz)
        _parts = text.split()
        _lw = (_parts[-1] if _parts else text).strip().lower()
        if _lw:
            all_suggestions = [s for s in all_suggestions if s.text.strip().lower() != _lw]
        
        # 9.4. Sonuçları birleştir ve sırala
        unique_suggestions = self._merge_and_rank(all_suggestions, max_suggestions)
        
        # 9.5. WHATSAPP BENZERİ: EĞER HİÇ ÖNERİ YOKSA, ZORUNLU ÖNERİ VER! (GARANTİLİ FALLBACK)
        if not unique_suggestions and len(text.strip()) >= 1:
            words = text.split()
            last_word = words[-1] if words else text
            last_word = last_word.strip()
            
            if len(last_word) >= 1:
                try:
                    # WHATSAPP BENZERİ: 3 katmanlı fallback (garantili öneri)
                    # 1. Direkt local search yap (bypass tüm filtreler)
                    fallback_suggestions = await elasticsearch_predictor._local_search(last_word, max_suggestions * 5)
                    
                    # 2. Eğer hala yoksa, large dictionary'den direkt ara
                    if not fallback_suggestions and LARGE_DICT_AVAILABLE and large_dictionary:
                        try:
                            results = large_dictionary.search(last_word.lower(), max_suggestions * 5)
                            if results:
                                for result in results:
                                    fallback_suggestions.append(Suggestion(
                                        text=result['word'],
                                        type="dictionary",
                                        score=result.get('score', 8.0),
                                        description=f"Sözlük (frekans: {result.get('frequency', 0)})",
                                        source="large_dictionary_fallback"
                                    ))
                        except Exception as e:
                            print(f"[WARNING] Large dict fallback hatasi: {e}")
                    
                    # 3. Eğer hala yoksa, varsayılan sözlükten ara
                    if not fallback_suggestions:
                        for word in elasticsearch_predictor.local_dictionary[:max_suggestions * 5]:
                            word_lower = word.lower()
                            if word_lower.startswith(last_word.lower()) and word_lower != last_word.lower():
                                fallback_suggestions.append(Suggestion(
                                    text=word,
                                    type="dictionary",
                                    score=8.0,
                                    description="Sözlük (varsayılan)",
                                    source="default_dictionary"
                                ))
                                if len(fallback_suggestions) >= max_suggestions:
                                    break
                    
                    if fallback_suggestions:
                        unique_suggestions = fallback_suggestions
                        if 'local_dictionary' not in sources_used:
                            sources_used.append('local_dictionary')
                except Exception as e:
                    print(f"[ERROR] Zorunlu arama hatasi: {e}")
                    import traceback
                    traceback.print_exc()
        
        # 10. Gelişmiş Ranking (final sıralama - YENİ!)
        if ADVANCED_RANKING_AVAILABLE and advanced_ranking and unique_suggestions:
            try:
                suggestions_dict = []
                for s in unique_suggestions:
                    if isinstance(s, dict):
                         suggestions_dict.append(s)
                    else:
                         suggestions_dict.append({
                            'text': getattr(s, 'text', ''),
                            'score': getattr(s, 'score', 0.0),
                            'type': getattr(s, 'type', 'unknown'),
                            'source': getattr(s, 'source', 'unknown'),
                            'description': getattr(s, 'description', '')
                        })
                
                ranked = advanced_ranking.rank_suggestions(suggestions_dict, context, user_id, text)
                if ranked and isinstance(ranked, list):
                    unique_suggestions = [Suggestion(**s) for s in ranked[:max_suggestions] if isinstance(s, dict)]
            except Exception as e:
                print(f"[WARNING] Advanced ranking hatasi: {e}")
        
        # İşlem süresi
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = PredictionResponse(
            suggestions=unique_suggestions,
            corrected_text=corrected_text,
            processing_time_ms=round(processing_time, 2),
            sources_used=sources_used
        )
        
        # WHATSAPP BENZERİ: Cache'e kaydetme - Devre dışı (her karakter için yeni öneri)
        # WhatsApp iPhone gibi çalışması için cache kullanma
        # if not skip_cache and REDIS_AVAILABLE and cache and cache_key:
        #     try:
        #         response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        #         cache.set(cache_key, response_dict, ttl=3600)
        #     except Exception as e:
        #         print(f"[WARNING] Cache kaydetme hatasi: {e}")
        
        return response
    
    async def _get_ai_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        """AI tahminlerini al"""
        try:
            suggestions = await transformer_predictor.predict(text, max_suggestions)
            if suggestions:
                sources_used.append("transformer")
            return suggestions
        except Exception as e:
            print(f"AI tahmin hatası: {e}")
            return []
    
    async def _get_trie_predictions(self, prefix: str, max_suggestions: int, sources_used: List[str]):
        """Trie Index ile ultra hızlı arama"""
        suggestions = []
        
        if TRIE_AVAILABLE and trie_index and hasattr(trie_index, 'word_count') and trie_index.word_count > 0:
            try:
                results = trie_index.search(prefix, max_suggestions)
                for result in results:
                    if isinstance(result, dict):
                        suggestions.append(Suggestion(
                            text=result.get('word', ''),
                            type=result.get('type', 'dictionary'),
                            score=result.get('score', 8.0),
                            description=result.get('description', 'Sözlük (Trie)'),
                            source=result.get('source', 'trie_index')
                        ))
                if suggestions:
                    sources_used.append('trie_index')
            except Exception as e:
                print(f"[WARNING] Trie search hatasi: {e}")
        
        return suggestions
    
    async def _get_search_predictions(self, prefix: str, max_suggestions: int, sources_used: List[str]):
        """Sözlük arama sonuçlarını al - TEK HARF İÇİN DE ÇALIŞIR! - GARANTİLİ!"""
        try:
            # Prefix boş değilse ara
            prefix = prefix.strip() if prefix else ""
            if not prefix or len(prefix) == 0:
                return []
            
            # GARANTİLİ: Her zaman local search yap
            suggestions = await elasticsearch_predictor.search(prefix, max_suggestions)
            
            # Eğer öneri yoksa, direkt large dictionary'den ara
            if not suggestions and LARGE_DICT_AVAILABLE and large_dictionary:
                try:
                    results = large_dictionary.search(prefix.lower(), max_suggestions)
                    if results:
                        for result in results:
                            suggestions.append(Suggestion(
                                text=result['word'],
                                type="dictionary",
                                score=result.get('score', 8.0),
                                description=f"Sözlük (frekans: {result.get('frequency', 0)})",
                                source="large_dictionary"
                            ))
                except Exception as e:
                    print(f"[WARNING] Large dictionary direct search hatasi: {e}")
            
            if suggestions:
                source_name = "elasticsearch" if elasticsearch_predictor.es_client else "local_dictionary"
                if source_name not in sources_used:
                    sources_used.append(source_name)
            
            return suggestions
        except Exception as e:
            print(f"[ERROR] Sözlük arama hatası: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _get_direct_large_dict_predictions(self, prefix: str, max_suggestions: int, sources_used: List[str]):
        """Large dictionary'den direkt arama - tum prefix uzunluklari"""
        suggestions = []
        try:
            if LARGE_DICT_AVAILABLE and large_dictionary:
                results = large_dictionary.search(prefix.lower(), max_suggestions)
                if results:
                    for result in results:
                        suggestions.append(Suggestion(
                            text=result['word'],
                            type="dictionary",
                            score=result.get('score', 9.0),
                            description=f"Sözlük (frekans: {result.get('frequency', 0)})",
                            source="large_dictionary_direct"
                        ))
                    if suggestions and 'large_dictionary_direct' not in sources_used:
                        sources_used.append('large_dictionary_direct')
        except Exception as e:
            print(f"[WARNING] Direct large dict search hatasi: {e}")
        return suggestions
    
    async def _get_ngram_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        """N-gram tahminlerini al"""
        try:
            if ADVANCED_NGRAM_AVAILABLE and advanced_ngram and hasattr(advanced_ngram, 'predict_next_word'):
                results = advanced_ngram.predict_next_word(text, max_suggestions)
                suggestions = []
                if results and isinstance(results, list):
                    for result in results:
                        if not isinstance(result, dict):
                            continue
                        txt = result.get('text') or result.get('word', '')
                        if not txt:
                            continue
                        suggestions.append(Suggestion(
                            text=txt,
                            type=result.get('type', 'ngram'),
                            score=result.get('score', 8.5),
                            description=result.get('description', 'N-gram tahmini'),
                            source=result.get('source', 'advanced_ngram')
                        ))
                if suggestions:
                    sources_used.append("advanced_ngram")
                return suggestions
            return []
        except Exception as e:
            print(f"[WARNING] N-gram prediction hatasi: {e}")
            return []
    
    async def _get_phrase_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        """Phrase completion tahminlerini al"""
        try:
            if PHRASE_COMPLETION_AVAILABLE and phrase_completer and hasattr(phrase_completer, 'complete_phrase'):
                results = phrase_completer.complete_phrase(text, max_suggestions)
                suggestions = []
                if results and isinstance(results, list):
                    for result in results:
                        if isinstance(result, dict) and 'text' in result:
                            suggestions.append(Suggestion(
                                text=result['text'],
                                type=result.get('type', 'phrase'),
                                score=result.get('score', 8.0),
                                description=result.get('description', 'Cümle tamamlama'),
                                source=result.get('source', 'phrase_completion')
                            ))
                if suggestions:
                    sources_used.append("phrase_completion")
                return suggestions
            return []
        except Exception as e:
            print(f"[WARNING] Phrase completion hatasi: {e}")
            return []
    
    async def _get_domain_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        """Domain-specific tahminlerini al"""
        try:
            if DOMAIN_DICT_AVAILABLE and domain_manager and hasattr(domain_manager, 'get_suggestions'):
                words = text.split()
                last_word = words[-1] if words else text
                context = None
                if CONTEXT_ANALYZER_AVAILABLE and context_analyzer and hasattr(context_analyzer, 'analyze'):
                    try:
                        context_analysis = context_analyzer.analyze(text)
                        if context_analysis and isinstance(context_analysis, dict):
                            # Context'ten domain çıkar
                            if context_analysis.get('topic') == 'customer_service':
                                context = 'customer_service'
                            elif context_analysis.get('topic') == 'technical':
                                context = 'technical'
                            elif context_analysis.get('topic') == 'ecommerce':
                                context = 'ecommerce'
                    except Exception as e:
                        print(f"[WARNING] Context analysis hatasi: {e}")
                
                results = domain_manager.get_suggestions(last_word, context, max_suggestions)
                suggestions = []
                if results and isinstance(results, list):
                    for result in results:
                        if isinstance(result, dict) and 'text' in result:
                            suggestions.append(Suggestion(
                                text=result['text'],
                                type=result.get('type', 'domain'),
                                score=result.get('score', 8.5),
                                description=result.get('description', 'Domain sözlüğü'),
                                source=result.get('source', 'domain_dict')
                            ))
                if suggestions:
                    sources_used.append("domain_dict")
                return suggestions
            return []
        except Exception as e:
            print(f"[WARNING] Domain dictionary hatasi: {e}")
            return []
    
    async def _get_emoji_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        """Emoji önerilerini al"""
        try:
            if EMOJI_AVAILABLE and emoji_suggester and hasattr(emoji_suggester, 'suggest_emojis'):
                results = emoji_suggester.suggest_emojis(text, max_suggestions)
                suggestions = []
                if results and isinstance(results, list):
                    for result in results:
                        if isinstance(result, dict) and 'text' in result:
                            suggestions.append(Suggestion(
                                text=result['text'],
                                type=result.get('type', 'emoji'),
                                score=result.get('score', 8.0),
                                description=result.get('description', 'Emoji önerisi'),
                                source=result.get('source', 'emoji')
                            ))
                if suggestions:
                    sources_used.append("emoji")
                return suggestions
            return []
        except Exception as e:
            print(f"[WARNING] Emoji suggestion hatasi: {e}")
            return []
    
    async def _get_template_predictions(self, text: str, max_suggestions: int, sources_used: List[str]):
        """Smart template önerilerini al"""
        try:
            if SMART_TEMPLATES_AVAILABLE and smart_template_manager and hasattr(smart_template_manager, 'get_templates'):
                # Sadece "/" ile başlayan veya template kelimeleri için
                if text.startswith('/') or any(word in text.lower() for word in ['sipariş', 'müşteri', 'api', 'database']):
                    results = smart_template_manager.get_templates(text, max_suggestions)
                    suggestions = []
                    if results and isinstance(results, list):
                        for result in results:
                            if isinstance(result, dict) and 'text' in result:
                                suggestions.append(Suggestion(
                                    text=result['text'],
                                    type=result.get('type', 'template'),
                                    score=result.get('score', 9.0),
                                    description=result.get('description', 'Akıllı şablon'),
                                    source=result.get('source', 'smart_templates')
                                ))
                    if suggestions:
                        sources_used.append("smart_templates")
                    return suggestions
            return []
        except Exception as e:
            print(f"[WARNING] Smart template hatasi: {e}")
            return []
    
    def _merge_and_rank(self, suggestions: List[Suggestion], max_suggestions: int) -> List[Suggestion]:
        """Sonuçları birleştir ve sırala - iPhone benzeri yaygın kelime önceliği"""
        if not suggestions:
            return []
        
        # Duplikatları kaldır
        seen = set()
        unique_suggestions = []
        
        for sug in suggestions:
            if not sug or not sug.text:
                continue
            key = sug.text.lower().strip()
            if not key:
                continue
                
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(sug)
            else:
                # Duplikat varsa skoru artır (daha iyi kaynak öncelikli)
                existing = next((s for s in unique_suggestions if s.text.lower() == key), None)
                if existing:
                    existing.score = max(existing.score, sug.score) + 0.5
        
        # iPhone benzeri: yaygın kelimelere skor bonusu (hangi, merhaba, nasıl vb. öne çıkar)
        if COMMON_WORDS_AVAILABLE and is_common and first_word_common:
            for s in unique_suggestions:
                t = (s.text or "").strip()
                if not t:
                    continue
                if " " not in t and is_common(t):
                    s.score += 3.5
                elif first_word_common(t):
                    s.score += 2.0
        
        # Skora göre sırala (en yüksek skorlu öneriler önce)
        unique_suggestions.sort(key=lambda x: x.score, reverse=True)
        
        return unique_suggestions[:max_suggestions]

orchestrator = HybridOrchestrator()

# ============================================
# RATE LIMITING
# ============================================

# Rate limiting için basit cache
_rate_limit_cache = {}
_rate_limit_window = 60  # 60 saniye
_rate_limit_max_requests = 100  # Dakikada maksimum 100 istek

def _check_rate_limit(user_id: str) -> bool:
    """Rate limiting kontrolü"""
    import time
    current_time = time.time()
    
    # Eski kayıtları temizle
    _rate_limit_cache[user_id] = [
        req_time for req_time in _rate_limit_cache.get(user_id, [])
        if current_time - req_time < _rate_limit_window
    ]
    
    # İstek sayısını kontrol et
    if len(_rate_limit_cache.get(user_id, [])) >= _rate_limit_max_requests:
        return False
    
    # Yeni isteği ekle
    if user_id not in _rate_limit_cache:
        _rate_limit_cache[user_id] = []
    _rate_limit_cache[user_id].append(current_time)
    
    return True

# WHATSAPP BENZERİ: WebSocket rate limiting çok esnek (her karakter için öneri)
_ws_rate_limit = {}
_ws_rate_limit_window = 60
_ws_rate_limit_max_requests = 1000  # WhatsApp benzeri: Dakikada maksimum 1000 istek (her karakter için)

def _check_ws_rate_limit(user_id: str) -> bool:
    """WebSocket rate limiting kontrolü"""
    import time
    current_time = time.time()
    
    _ws_rate_limit[user_id] = [
        req_time for req_time in _ws_rate_limit.get(user_id, [])
        if current_time - req_time < _ws_rate_limit_window
    ]
    
    if len(_ws_rate_limit.get(user_id, [])) >= _ws_rate_limit_max_requests:
        return False
    
    if user_id not in _ws_rate_limit:
        _ws_rate_limit[user_id] = []
    _ws_rate_limit[user_id].append(current_time)
    
    return True

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    return {
        "message": "TextHelper ULTIMATE API",
        "version": "2.0.0",
        "status": "running",
        "architecture": "Hybrid: Transformer + Elasticsearch + FastAPI",
        "features": [
            "Transformer AI Predictions",
            "Elasticsearch Dictionary Search",
            "Hybrid Orchestration",
            "Spell Checking",
            "WebSocket Support"
        ],
        "endpoints": {
            "predict": "/predict",
            "websocket": "/ws",
            "learn": "/learn",
            "health": "/health",
            "docs": "/docs"
        }
    }

# Rate limiting için basit cache
_rate_limit_cache = {}
_rate_limit_window = 60  # 60 saniye
_rate_limit_max_requests = 100  # Dakikada maksimum 100 istek

def _check_rate_limit(user_id: str) -> bool:
    """Rate limiting kontrolü"""
    import time
    current_time = time.time()
    
    # Eski kayıtları temizle
    _rate_limit_cache[user_id] = [
        req_time for req_time in _rate_limit_cache.get(user_id, [])
        if current_time - req_time < _rate_limit_window
    ]
    
    # İstek sayısını kontrol et
    if len(_rate_limit_cache.get(user_id, [])) >= _rate_limit_max_requests:
        return False
    
    # Yeni isteği ekle
    if user_id not in _rate_limit_cache:
        _rate_limit_cache[user_id] = []
    _rate_limit_cache[user_id].append(current_time)
    
    return True

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest, req: Request, user_id: str = "default"):
    """
    Hybrid tahmin endpoint'i
    Transformer + Elasticsearch sonuçlarını birleştirir
    """
    # Rate limiting kontrolü (basit)
    if not _check_rate_limit(user_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit aşıldı. Maksimum {_rate_limit_max_requests} istek/{_rate_limit_window} saniye"
        )
    
    # Security: Input validation
    if SECURITY_AVAILABLE and security_manager:
        try:
            is_valid, error_msg = security_manager.validate_input(request.text)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg or "Invalid input")
            
            # Rate limiting
            client_ip = req.client.host if req.client else "unknown"
            if not security_manager.check_rate_limit(client_ip):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            # Sanitize input
            request.text = security_manager.sanitize_input(request.text)
        except HTTPException:
            raise
        except Exception as e:
            print(f"[WARNING] Security check hatasi: {e}")
    
    print(f"[DEBUG] API Request: text='{request.text}'", flush=True)
    response = await orchestrator.predict(
        text=request.text,
        max_suggestions=request.max_suggestions,
        use_ai=request.use_ai,
        use_search=request.use_search,
        user_id=user_id
    )
    
    # ML öğrenme (kullanıcı seçimini bekliyoruz)
    # Bu endpoint'te sadece tahmin yapıyoruz
    
    return response

# WHATSAPP BENZERİ: WebSocket rate limiting çok esnek (her karakter için öneri)
_ws_rate_limit = {}
_ws_rate_limit_window = 60
_ws_rate_limit_max_requests = 1000  # WhatsApp benzeri: Dakikada maksimum 1000 istek (her karakter için)

def _check_ws_rate_limit(user_id: str) -> bool:
    """WebSocket rate limiting kontrolü"""
    import time
    current_time = time.time()
    
    _ws_rate_limit[user_id] = [
        req_time for req_time in _ws_rate_limit.get(user_id, [])
        if current_time - req_time < _ws_rate_limit_window
    ]
    
    if len(_ws_rate_limit.get(user_id, [])) >= _ws_rate_limit_max_requests:
        return False
    
    if user_id not in _ws_rate_limit:
        _ws_rate_limit[user_id] = []
    _ws_rate_limit[user_id].append(current_time)
    
    return True

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket ile real-time öneriler - WHATSAPP BENZERİ (her karakter için anlık öneri)"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # WHATSAPP BENZERİ: Rate limiting daha esnek (her karakter için öneri)
            user_id = data.get("user_id", "default")
            if not _check_ws_rate_limit(user_id):
                await websocket.send_json({
                    "error": f"Rate limit aşıldı. Maksimum {_ws_rate_limit_max_requests} istek/{_ws_rate_limit_window} saniye"
                })
                continue
            
            text = data.get("text", "").strip()
            context_message = data.get("context_message", None) # YENİ
            max_suggestions = data.get("max_suggestions", 80)
            use_ai = data.get("use_ai", True)
            use_search = data.get("use_search", True)
            
            try:
                # WHATSAPP BENZERİ: Her karakter için anlık öneri (cache yok)
                # "a" -> "ak" -> "akı" -> "akıl" her adımda güncelleniyor
                print(f"[DEBUG] WS Request: text='{text}', context='{context_message}'", flush=True)
                response = await orchestrator.predict(
                    text=text,
                    context_message=context_message, # YENİ
                    max_suggestions=max_suggestions,
                    use_ai=use_ai,
                    use_search=use_search,
                    user_id=user_id
                )
                
                # WHATSAPP BENZERİ: Anlık gönder (her karakter için)
                response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
                await websocket.send_json(response_dict)
            except Exception as e:
                print(f"[ERROR] Prediction loop hatasi: {e}", flush=True)
                # Client'a hata mesajı gönder ama bağlantıyı koparma
                await websocket.send_json({"suggestions": [], "error": str(e)})
            
    except WebSocketDisconnect:
        # Normal disconnect - client bağlantıyı kapattı
        print("connection closed (normal)")
    except Exception as e:
        # Diğer hatalar
        error_code = getattr(e, 'code', None)
        if error_code == 1001 or "disconnect" in str(e).lower():
            # 1001 = normal disconnect (client kapattı)
            print("connection closed (normal)")
        else:
            print(f"WebSocket error: {e}")
            # Sadece bağlantı hala açıksa kapat
            try:
                if websocket.client_state.name != "DISCONNECTED":
                    await websocket.close()
            except Exception:
                pass  # Zaten kapatılmış

@app.post("/learn")
async def learn_text(text: str, user_id: str = "default", selected_suggestion: Optional[str] = None):
    """Sistem öğrenme endpoint'i - Real-time learning"""
    # 1. ML Learning'den öğren
    if ML_LEARNING_AVAILABLE and ml_learning and hasattr(ml_learning, 'learn_from_interaction'):
        try:
            ml_learning.learn_from_interaction(
                user_id=user_id,
                input_text=text,
                selected_suggestion=selected_suggestion or "",
                context=text
            )
            print(f"[LEARN] ML ogrenme: {text} (kullanici: {user_id})")
        except Exception as e:
            print(f"[WARNING] ML learning hatasi: {e}")
    
    # 2. N-gram'dan öğren (YENİ!)
    if ADVANCED_NGRAM_AVAILABLE and advanced_ngram and hasattr(advanced_ngram, 'learn_from_text'):
        try:
            advanced_ngram.learn_from_text(text)
            if selected_suggestion:
                # Seçilen öneriyi de öğren
                full_text = f"{text} {selected_suggestion}"
                advanced_ngram.learn_from_text(full_text)
            print(f"[LEARN] N-gram ogrenme: {text}")
        except Exception as e:
            print(f"[WARNING] N-gram learning hatasi: {e}")
    
    # 3. Ranking'den öğren (YENİ!)
    if ADVANCED_RANKING_AVAILABLE and advanced_ranking and selected_suggestion and hasattr(advanced_ranking, 'record_click'):
        try:
            advanced_ranking.record_click(selected_suggestion)
            print(f"[LEARN] Ranking ogrenme: {selected_suggestion}")
        except Exception as e:
            print(f"[WARNING] Ranking learning hatasi: {e}")
    
    # Cache'i temizle (yeni öğrenilen bilgiler için)
    if REDIS_AVAILABLE and cache and hasattr(cache, 'clear_pattern'):
        try:
            cache.clear_pattern("predict:*")
        except Exception as e:
            print(f"[WARNING] Cache clear hatasi: {e}")
    
    return {"status": "learned", "text": text, "user_id": user_id, "real_time": True}

@app.get("/health")
async def health():
    """Sistem sağlık kontrolü - Detaylı Durum"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0",
        "components": {}
    }
    
    # 1. Dictionary Status
    dict_size = 0
    if elasticsearch_predictor.local_dictionary:
        dict_size = len(elasticsearch_predictor.local_dictionary)
    
    if LARGE_DICT_AVAILABLE and large_dictionary:
        try:
            dict_size = large_dictionary.get_word_count()
        except:
            pass
            
    health_status["components"]["dictionary"] = {"status": "ok", "size": dict_size}
    
    # 2. Transformer Status
    if REAL_TRANSFORMER_AVAILABLE and transformer_model:
        try:
            info = transformer_model.get_model_info()
            health_status["components"]["transformer"] = {
                "status": "active" if info.get("loaded") else "standby",
                "details": info
            }
        except Exception as e:
            health_status["components"]["transformer"] = {"status": "error", "error": str(e)}
    else:
         health_status["components"]["transformer"] = {"status": "disabled"}
            
    # 3. Redis Status
    if REDIS_AVAILABLE and cache:
        health_status["components"]["redis"] = {"status": "connected", "type": "redis-py"}
    else:
        health_status["components"]["redis"] = {"status": "unavailable"}
             
    # 4. Elasticsearch Status
    if elasticsearch_predictor.es_client:
         health_status["components"]["elasticsearch"] = {"status": "connected"}
    else:
         health_status["components"]["elasticsearch"] = {"status": "disconnected"}
         
    return health_status

@app.post("/index_words")
async def index_words_to_elasticsearch():
    """Kelimeleri Elasticsearch'e index'le"""
    if not ES_MANAGER_AVAILABLE or not es_manager or not hasattr(es_manager, 'available') or not es_manager.available:
        return {"status": "error", "message": "Elasticsearch kullanılamıyor"}
    
    # Kelimeleri hazırla
    words_data = []
    
    # Büyük sözlükten al
    if LARGE_DICT_AVAILABLE and large_dictionary:
        for word in large_dictionary.words:
            words_data.append({
                'word': word,
                'frequency': large_dictionary.word_frequencies.get(word.lower(), 1),
                'category': 'general'
            })
    else:
        # Varsayılan sözlük
        for word in elasticsearch_predictor.local_dictionary:
            words_data.append({
                'word': word,
                'frequency': 1,
                'category': 'general'
            })
    
    # Index'le
    success = False
    if hasattr(es_manager, 'index_words'):
        try:
            success = await es_manager.index_words(words_data)
        except Exception as e:
            print(f"[ERROR] Index hatasi: {e}")
            return {"status": "error", "message": f"Index hatasi: {e}"}
    
    return {
        "status": "success" if success else "error",
        "words_indexed": len(words_data) if success else 0
    }

# ============================================
# BAŞLATMA
# ============================================

# ============================================
# LIFESPAN (YENİ - Startup/Shutdown)
# ============================================


from fastapi import BackgroundTasks

def background_learn(user_id: str, text: str, selected_suggestion: str):
    """Arka planda öğrenme işlemi"""
    if ML_LEARNING_AVAILABLE and ml_learning:
        try:
            ml_learning.learn_from_interaction(
                user_id,
                text,
                selected_suggestion
            )
        except Exception as e:
            logger.error(f"Background learning hatası: {e}")

@app.post("/learn")
async def learn_interaction(feedback: FeedbackRequest, background_tasks: BackgroundTasks):
    """Kullanıcı etkileşiminden öğren (Fire-and-Forget)"""
    if ML_LEARNING_AVAILABLE and ml_learning:
        # Ana thread'i bekletmeden arka plana at
        background_tasks.add_task(
            background_learn,
            feedback.user_id,
            feedback.text,
            feedback.selected_suggestion
        )
        return {"status": "queued"}
    return {"status": "unavailable"}

# ============================================
# API VERSIONING (Standardization)
# ============================================

class CorrectionRequest(BaseModel):
    text: str
    user_id: Optional[str] = "default"

@app.post("/correct")
async def autocorrect_text(request: CorrectionRequest):
    """
    iPhone/WhatsApp tarzı agresif otomatik düzeltme.
    Fuzzy search + N-Gram context kullanır.
    """
    original = request.text
    corrected = original
    
    # Kelimeleri ayır
    words = original.split()
    if not words:
        return {"original": original, "corrected": original, "changed": False}
        
    # Son kelimeyi düzelt (genelde yazılmakta olan)
    last_word = words[-1]
    
    # 1. Fuzzy Search ile en iyi eşleşmeyi bul
    if ADVANCED_FUZZY_AVAILABLE and advanced_fuzzy:
        suggestions = advanced_fuzzy.match(last_word, elasticsearch_predictor.local_dictionary if elasticsearch_predictor.local_dictionary else [], max_results=1)
        if suggestions and suggestions[0]['confidence'] > 0.8:  # Yüksek güvenilirlik
             words[-1] = suggestions[0]['word']
             corrected = " ".join(words)
    
    # 2. N-Gram Context ile kontrol et (daha akıllı düzeltme)
    # Gelecekte eklenebilir: "merhaba nasılsın" gibi ikilileri kontrol et
             
    changed = corrected != original
    return {"original": original, "corrected": corrected, "changed": changed}

# V1 Router oluştur ve mevcut fonksiyonları bağla
router_v1 = APIRouter(prefix="/api/v1", tags=["v1"])

# Existing handlers bound to v1
router_v1.add_api_route("/predict", predict, methods=["POST"], response_model=PredictionResponse)
router_v1.add_api_route("/learn", learn_interaction, methods=["POST"])
router_v1.add_api_route("/health", health, methods=["GET"])
router_v1.add_api_route("/correct", autocorrect_text, methods=["POST"]) # YENI

app.include_router(router_v1)

if __name__ == "__main__":
    # Production: reloader kapalı (2x RAM tasarrufu)
    # Development: DEV_MODE=true ile aç
    is_dev = os.getenv("DEV_MODE", "false").lower() == "true"
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=is_dev  # Sadece geliştirme modunda aç
    )

