"""
Elasticsearch Gerçek Entegrasyonu
Büyük sözlükler için hızlı arama
"""

import os
from typing import List, Dict
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

class ElasticsearchManager:
    """Elasticsearch yöneticisi"""
    
    def __init__(self):
        self.es_client = None
        self.index_name = "turkish_words"
        self.available = False
        self.host = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
        
    async def connect(self):
        """Elasticsearch'e bağlan"""
        try:
            self.es_client = Elasticsearch(
                [self.host],
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
            
            # Bağlantı testi
            if self.es_client.ping():
                self.available = True
                print(f"[OK] Elasticsearch baglantisi kuruldu: {self.host}")
                
                # Index oluştur (yoksa)
                await self._create_index()
            else:
                print("[WARNING] Elasticsearch'e baglanilamadi")
                self.available = False
                
        except ImportError:
            print("[WARNING] elasticsearch kutuphanesi kurulu degil")
            print("   Kurulum: pip install elasticsearch")
            self.available = False
        except Exception as e:
            print(f"[WARNING] Elasticsearch baglanti hatasi: {e}")
            self.available = False
    
    async def _create_index(self):
        """Index oluştur"""
        if not self.es_client or not self.available:
            return
        
        try:
            # Index var mı kontrol et
            if self.es_client.indices.exists(index=self.index_name):
                print(f"[OK] Index zaten mevcut: {self.index_name}")
                return
            
            # Index oluştur
            index_body = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "turkish_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": [
                                    "lowercase",
                                    "turkish_stop",
                                    "turkish_lowercase",
                                    "turkish_stemmer"
                                ]
                            }
                        },
                        "filter": {
                            "turkish_stop": {
                                "type": "stop",
                                "stopwords": "_turkish_"
                            },
                            "turkish_lowercase": {
                                "type": "lowercase",
                                "language": "turkish"
                            },
                            "turkish_stemmer": {
                                "type": "stemmer",
                                "language": "turkish"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "word": {
                            "type": "text",
                            "analyzer": "turkish_analyzer",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                },
                                "suggest": {
                                    "type": "completion",
                                    "analyzer": "simple"
                                }
                            }
                        },
                        "frequency": {
                            "type": "integer"
                        },
                        "category": {
                            "type": "keyword"
                        }
                    }
                }
            }
            
            self.es_client.indices.create(index=self.index_name, body=index_body)
            print(f"[OK] Index olusturuldu: {self.index_name}")
            
        except Exception as e:
            print(f"Index oluşturma hatası: {e}")
    
    async def index_words(self, words: List[Dict]):
        """Kelimeleri index'e ekle"""
        if not self.es_client or not self.available:
            return False
        
        try:
            actions = []
            for i, word_data in enumerate(words):
                action = {
                    "_index": self.index_name,
                    "_id": i,
                    "_source": {
                        "word": word_data.get('word', ''),
                        "frequency": word_data.get('frequency', 1),
                        "category": word_data.get('category', 'general'),
                        "word_suggest": {
                            "input": [word_data.get('word', '')],
                            "weight": word_data.get('frequency', 1)
                        }
                    }
                }
                actions.append(action)
            
            # Bulk insert
            success, failed = bulk(self.es_client, actions, chunk_size=1000)
            print(f"[OK] {success} kelime index'lendi, {len(failed)} hata")
            return True
            
        except Exception as e:
            print(f"Index'leme hatası: {e}")
            return False
    
    async def search(self, prefix: str, max_results: int = 10) -> List[Dict]:
        """Prefix ile arama"""
        if not self.es_client or not self.available:
            return []
        
        try:
            # Completion suggester query
            query = {
                "suggest": {
                    "word-suggest": {
                        "prefix": prefix.lower(),
                        "completion": {
                            "field": "word_suggest",
                            "size": max_results,
                            "fuzzy": {
                                "fuzziness": 1
                            }
                        }
                    }
                }
            }
            
            response = self.es_client.search(index=self.index_name, body=query)
            
            suggestions = []
            options = response.get('suggest', {}).get('word-suggest', [{}])[0].get('options', [])
            
            for option in options:
                word = option['text']
                score = option.get('score', 0)
                frequency = option.get('_source', {}).get('frequency', 1)
                
                suggestions.append({
                    'word': word,
                    'score': 8.0 + (score / 100) + (frequency / 1000),
                    'type': 'dictionary',
                    'description': f'Sözlük (Elasticsearch, frekans: {frequency})',
                    'source': 'elasticsearch'
                })
            
            return suggestions
            
        except Exception as e:
            print(f"Elasticsearch arama hatası: {e}")
            return []
    
    async def fuzzy_search(self, word: str, max_results: int = 5) -> List[Dict]:
        """Fuzzy search"""
        if not self.es_client or not self.available:
            return []
        
        try:
            query = {
                "query": {
                    "fuzzy": {
                        "word": {
                            "value": word.lower(),
                            "fuzziness": 2,
                            "prefix_length": 1
                        }
                    }
                },
                "size": max_results
            }
            
            response = self.es_client.search(index=self.index_name, body=query)
            
            suggestions = []
            for hit in response['hits']['hits']:
                word_data = hit['_source']
                suggestions.append({
                    'word': word_data['word'],
                    'score': hit['_score'] * 0.5,
                    'type': 'fuzzy',
                    'description': 'Fuzzy match (Elasticsearch)',
                    'source': 'elasticsearch'
                })
            
            return suggestions
            
        except Exception as e:
            print(f"Fuzzy search hatası: {e}")
            return []

# Global instance
es_manager = ElasticsearchManager()
