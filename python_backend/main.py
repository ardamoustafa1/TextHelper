"""
TextHelper ULTIMATE - Hybrid: Transformer + Elasticsearch + FastAPI
En iyi çözüm - Production ready
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import asyncio
from datetime import datetime
import json
import os
import sys

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

# ============================================
# KONFIGÜRASYON
# ============================================

app = FastAPI(
    title="TextHelper ULTIMATE API",
    version="2.0.0",
    description="Hybrid: Transformer AI + Elasticsearch + FastAPI - En iyi otomatik tamamlama sistemi"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# MODELLER
# ============================================

class PredictionRequest(BaseModel):
    text: str
    max_suggestions: Optional[int] = 7
    use_ai: Optional[bool] = True
    use_search: Optional[bool] = True

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
        # Gerçek transformer modeli kullan (varsa)
        if REAL_TRANSFORMER_AVAILABLE and transformer_model:
            await transformer_model.load_model()
            self.model_loaded = transformer_model.model_loaded
            if self.model_loaded:
                print("[OK] Gercek Transformer modeli yuklendi")
                return
        
        # Fallback: Pattern-based
        if not self.use_transformer:
            print("[WARNING] Transformer kullanimi devre disi (USE_TRANSFORMER=true ile aktif edin)")
            return
            
        try:
            # Hugging Face transformers
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            print("[INFO] Transformer modeli yukleniyor...")
            model_name = "dbmdz/bert-base-turkish-cased"
            
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
        self.local_dictionary = self._load_dictionary()
        
    def _load_dictionary(self) -> List[str]:
        """Yerel sözlük yükle (Elasticsearch yoksa)"""
        # Büyük Türkçe sözlük
        dictionary_file = os.path.join(os.path.dirname(__file__), "turkish_dictionary.txt")
        
        if os.path.exists(dictionary_file):
            with open(dictionary_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        
        # Varsayılan sözlük
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
            await es_manager.connect()
            self.es_client = es_manager.es_client if es_manager.available else None
            if es_manager.available:
                print("[OK] Elasticsearch Manager ile baglanti kuruldu")
                return
        
        # Fallback: Direkt bağlantı
        if not self.use_elasticsearch:
            return
        
        try:
            from elasticsearch import Elasticsearch
            
            es_host = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
            self.es_client = Elasticsearch([es_host])
            
            # Bağlantı testi
            if self.es_client.ping():
                print("[OK] Elasticsearch baglantisi kuruldu")
            else:
                print("[WARNING] Elasticsearch'e baglanilamadi, yerel sozluk kullanilacak")
                self.es_client = None
        except ImportError:
            print("[WARNING] elasticsearch kutuphanesi kurulu degil: pip install elasticsearch")
            self.es_client = None
        except Exception as e:
            print(f"[WARNING] Elasticsearch baglanti hatasi: {e}")
            self.es_client = None
    
    async def search(self, prefix: str, max_results: int = 10) -> List[Suggestion]:
        """Elasticsearch'te ara (veya yerel sözlükte)"""
        if self.es_client:
            return await self._elasticsearch_search(prefix, max_results)
        else:
            return await self._local_search(prefix, max_results)
    
    async def _elasticsearch_search(self, prefix: str, max_results: int) -> List[Suggestion]:
        """Elasticsearch ile ara"""
        # ES Manager kullan (varsa)
        if ES_MANAGER_AVAILABLE and es_manager and es_manager.available:
            results = await es_manager.search(prefix, max_results)
            return [Suggestion(**r) for r in results]
        
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
        """Yerel sözlükte ara"""
        suggestions = []
        prefix_lower = prefix.lower()
        
        # Büyük sözlük kullan (varsa)
        if LARGE_DICT_AVAILABLE and large_dictionary:
            results = large_dictionary.search(prefix_lower, max_results)
            for result in results:
                suggestions.append(Suggestion(
                    text=result['word'],
                    type="dictionary",
                    score=result['score'],
                    description=f"Sözlük (frekans: {result['frequency']})",
                    source="elasticsearch"
                ))
            return suggestions
        
        # Varsayılan sözlük
        for word in self.local_dictionary:
            word_lower = word.lower()
            
            # Prefix eşleşmesi
            if word_lower.startswith(prefix_lower) and word_lower != prefix_lower:
                # Skor: prefix uzunluğu ve kelime sırasına göre
                score = (len(prefix_lower) / len(word_lower)) * 8.0
                
                suggestions.append(Suggestion(
                    text=word,
                    type="dictionary",
                    score=score,
                    description="Sözlük",
                    source="elasticsearch"
                ))
        
        # Skora göre sırala
        suggestions.sort(key=lambda x: x.score, reverse=True)
        return suggestions[:max_results]

elasticsearch_predictor = ElasticsearchPredictor()

# ============================================
# 3. YAZIM DÜZELTME
# ============================================

class SpellChecker:
    """Yazım düzeltme"""
    
    def __init__(self):
        try:
            from autocorrect import Speller
            self.speller = Speller(lang='tr')
            self.available = True
        except ImportError:
            self.available = False
            print("[WARNING] autocorrect kurulu degil: pip install autocorrect")
    
    async def check(self, word: str) -> Optional[str]:
        """Yazım hatasını düzelt"""
        if not self.available or len(word) <= 3:
            return None
        
        try:
            corrected = self.speller(word)
            return corrected if corrected != word else None
        except:
            return None

spell_checker = SpellChecker()

# ============================================
# 4. HYBRID ORCHESTRATOR (BİRLEŞTİRME)
# ============================================

class HybridOrchestrator:
    """Transformer ve Elasticsearch sonuçlarını birleştir"""
    
    async def predict(
        self,
        text: str,
        max_suggestions: int = 7,
        use_ai: bool = True,
        use_search: bool = True,
        user_id: str = "default"
    ) -> PredictionResponse:
        """Hybrid tahmin yap"""
        start_time = datetime.now()
        sources_used = []
        all_suggestions = []
        
        # Cache kontrolü
        cache_key = None
        if REDIS_AVAILABLE and cache:
            cache_key = cache.generate_key("predict", text, max_suggestions, use_ai, use_search)
            cached_result = cache.get(cache_key)
            if cached_result:
                return PredictionResponse(**cached_result)
        
        # Paralel olarak her iki kaynaktan da al
        tasks = []
        
        # 1. AI Tahminleri (Transformer)
        if use_ai:
            tasks.append(self._get_ai_predictions(text, max_suggestions, sources_used))
        
        # 2. Sözlük Arama (Elasticsearch)
        if use_search:
            words = text.split()
            last_word = words[-1] if words else text
            tasks.append(self._get_search_predictions(last_word, max_suggestions, sources_used))
        
        # Paralel çalıştır
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Sonuçları birleştir
        for result in results:
            if isinstance(result, list):
                all_suggestions.extend(result)
        
        # 3. ML ile kişiselleştirme
        if ML_LEARNING_AVAILABLE and ml_learning:
            base_texts = [s.text for s in all_suggestions]
            personalized = ml_learning.get_personalized_suggestions(user_id, text, base_texts)
            
            # Kişiselleştirilmiş skorları uygula
            for sug in all_suggestions:
                personal = next((p for p in personalized if p['text'] == sug.text), None)
                if personal and personal.get('personalized'):
                    sug.score += personal['score'] * 0.3
        
        # 4. Yazım Düzeltme
        corrected_text = None
        if text:
            words = text.split()
            if words:
                corrected = await spell_checker.check(words[-1])
                if corrected:
                    corrected_text = ' '.join(words[:-1] + [corrected])
        
        # 5. Sonuçları birleştir ve sırala
        unique_suggestions = self._merge_and_rank(all_suggestions, max_suggestions)
        
        # İşlem süresi
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = PredictionResponse(
            suggestions=unique_suggestions,
            corrected_text=corrected_text,
            processing_time_ms=round(processing_time, 2),
            sources_used=sources_used
        )
        
        # Cache'e kaydet
        if REDIS_AVAILABLE and cache and cache_key:
            cache.set(cache_key, response.dict(), ttl=300)
        
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
    
    async def _get_search_predictions(self, prefix: str, max_suggestions: int, sources_used: List[str]):
        """Sözlük arama sonuçlarını al"""
        try:
            suggestions = await elasticsearch_predictor.search(prefix, max_suggestions)
            if suggestions:
                sources_used.append("elasticsearch")
            return suggestions
        except Exception as e:
            print(f"Sözlük arama hatası: {e}")
            return []
    
    def _merge_and_rank(self, suggestions: List[Suggestion], max_suggestions: int) -> List[Suggestion]:
        """Sonuçları birleştir ve sırala"""
        # Duplikatları kaldır
        seen = set()
        unique_suggestions = []
        
        for sug in suggestions:
            key = sug.text.lower()
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(sug)
            else:
                # Duplikat varsa skoru artır
                existing = next(s for s in unique_suggestions if s.text.lower() == key)
                existing.score = max(existing.score, sug.score) + 0.5
        
        # Skora göre sırala
        unique_suggestions.sort(key=lambda x: x.score, reverse=True)
        
        return unique_suggestions[:max_suggestions]

orchestrator = HybridOrchestrator()

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

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest, user_id: str = "default"):
    """
    Hybrid tahmin endpoint'i
    Transformer + Elasticsearch sonuçlarını birleştirir
    """
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket ile real-time öneriler"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            text = data.get("text", "")
            max_suggestions = data.get("max_suggestions", 7)
            use_ai = data.get("use_ai", True)
            use_search = data.get("use_search", True)
            
            # Tahmin yap
            response = await orchestrator.predict(
                text=text,
                max_suggestions=max_suggestions,
                use_ai=use_ai,
                use_search=use_search
            )
            
            # Gönder
            await websocket.send_json(response.dict())
            
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

@app.post("/learn")
async def learn_text(text: str, user_id: str = "default", selected_suggestion: Optional[str] = None):
    """Sistem öğrenme endpoint'i"""
    if ML_LEARNING_AVAILABLE and ml_learning:
        # ML sisteminden öğren
        ml_learning.learn_from_interaction(
            user_id=user_id,
            input_text=text,
            selected_suggestion=selected_suggestion or "",
            context=text
        )
        print(f"[LEARN] ML ogrenme: {text} (kullanici: {user_id})")
    
    # Cache'i temizle (yeni öğrenilen bilgiler için)
    if REDIS_AVAILABLE and cache:
        cache.clear_pattern("predict:*")
    
    return {"status": "learned", "text": text, "user_id": user_id}

@app.get("/health")
async def health():
    """Sistem sağlık kontrolü"""
    dict_size = len(elasticsearch_predictor.local_dictionary)
    if LARGE_DICT_AVAILABLE and large_dictionary:
        dict_size = large_dictionary.get_word_count()
    
    transformer_info = {}
    if REAL_TRANSFORMER_AVAILABLE and transformer_model:
        transformer_info = transformer_model.get_model_info()
    
    return {
        "status": "healthy",
        "transformer_loaded": transformer_predictor.model_loaded or (transformer_info.get("loaded", False)),
        "transformer_info": transformer_info,
        "elasticsearch_available": elasticsearch_predictor.es_client is not None or (ES_MANAGER_AVAILABLE and es_manager and es_manager.available),
        "spellchecker_available": spell_checker.available,
        "redis_available": REDIS_AVAILABLE and cache and (cache.available if hasattr(cache, 'available') else False),
        "ml_learning_available": ML_LEARNING_AVAILABLE,
        "large_dictionary_available": LARGE_DICT_AVAILABLE,
        "dictionary_size": dict_size
    }

@app.post("/index_words")
async def index_words_to_elasticsearch():
    """Kelimeleri Elasticsearch'e index'le"""
    if not ES_MANAGER_AVAILABLE or not es_manager or not es_manager.available:
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
    success = await es_manager.index_words(words_data)
    
    return {
        "status": "success" if success else "error",
        "words_indexed": len(words_data) if success else 0
    }

# ============================================
# BAŞLATMA
# ============================================

@app.on_event("startup")
async def startup_event():
    """Uygulama başlatıldığında"""
    print("=" * 60)
    print("=" * 60)
    print("TextHelper ULTIMATE - Hybrid System")
    print("Transformer + Elasticsearch + FastAPI")
    print("=" * 60)
    
    # Transformer modelini yükle
    await transformer_predictor.load_model()
    
    # Elasticsearch'e bağlan
    await elasticsearch_predictor.connect_elasticsearch()
    
    # ES Manager varsa kelimeleri index'le
    if ES_MANAGER_AVAILABLE and es_manager and es_manager.available:
        # İlk başlatmada kelimeleri index'le (opsiyonel)
        print("[INFO] Elasticsearch Manager aktif - kelimeleri index'lemek icin /index_words endpoint'ini kullanin")
    
    print("✅ Sistem hazır!")
    print("[INFO] API Docs: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws")
    print("=" * 60)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
