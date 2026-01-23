"""
Machine Learning Öğrenme Sistemi
Kullanıcı davranışından öğrenir
"""

from typing import List, Dict
from collections import defaultdict
import json
import os
from datetime import datetime

class MLLearningSystem:
    """ML tabanlı öğrenme sistemi"""
    
    def __init__(self):
        self.user_preferences = defaultdict(lambda: defaultdict(int))
        self.context_patterns = defaultdict(lambda: defaultdict(int))
        self.word_cooccurrence = defaultdict(lambda: defaultdict(int))
        self.load_data()
    
    def learn_from_interaction(
        self,
        user_id: str,
        input_text: str,
        selected_suggestion: str,
        context: str = ""
    ):
        """Kullanıcı etkileşiminden öğren"""
        # Kullanıcı tercihlerini güncelle
        self.user_preferences[user_id][selected_suggestion] += 1
        
        # Bağlam pattern'lerini öğren
        if context:
            self.context_patterns[context][selected_suggestion] += 1
        
        # Kelime birlikte kullanımını öğren
        words = input_text.split()
        if len(words) > 1:
            for i in range(len(words) - 1):
                self.word_cooccurrence[words[i]][words[i+1]] += 1
        
        # Periyodik olarak kaydet
        if len(self.user_preferences) % 10 == 0:
            self.save_data()
    
    def get_personalized_suggestions(
        self,
        user_id: str,
        text: str,
        base_suggestions: List[str]
    ) -> List[Dict]:
        """Kişiselleştirilmiş öneriler"""
        personalized = []
        
        # Kullanıcı tercihlerine göre skorla
        for suggestion in base_suggestions:
            base_score = 1.0
            user_pref = self.user_preferences[user_id].get(suggestion, 0)
            
            # Kullanıcı tercihi bonusu
            personalized_score = base_score + (user_pref * 0.5)
            
            personalized.append({
                'text': suggestion,
                'score': personalized_score,
                'personalized': user_pref > 0
            })
        
        # Skora göre sırala
        personalized.sort(key=lambda x: x['score'], reverse=True)
        return personalized
    
    def predict_next_word(self, context: str) -> List[str]:
        """Bağlamdan sonraki kelimeyi tahmin et"""
        words = context.split()
        if not words:
            return []
        
        last_word = words[-1].lower()
        next_words = self.word_cooccurrence.get(last_word, {})
        
        # En sık kullanılanları döndür
        sorted_words = sorted(
            next_words.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [word for word, count in sorted_words[:5]]
    
    def save_data(self):
        """Verileri kaydet"""
        data_file = os.path.join(
            os.path.dirname(__file__),
            "ml_learning_data.json"
        )
        
        try:
            data = {
                'user_preferences': dict(self.user_preferences),
                'context_patterns': dict(self.context_patterns),
                'word_cooccurrence': {
                    k: dict(v) for k, v in self.word_cooccurrence.items()
                },
                'last_updated': datetime.now().isoformat()
            }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"ML data kaydetme hatası: {e}")
    
    def load_data(self):
        """Verileri yükle"""
        data_file = os.path.join(
            os.path.dirname(__file__),
            "ml_learning_data.json"
        )
        
        if not os.path.exists(data_file):
            return
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                self.user_preferences = defaultdict(
                    lambda: defaultdict(int),
                    {k: defaultdict(int, v) for k, v in data.get('user_preferences', {}).items()}
                )
                
                self.context_patterns = defaultdict(
                    lambda: defaultdict(int),
                    {k: defaultdict(int, v) for k, v in data.get('context_patterns', {}).items()}
                )
                
                self.word_cooccurrence = defaultdict(
                    lambda: defaultdict(int),
                    {k: defaultdict(int, v) for k, v in data.get('word_cooccurrence', {}).items()}
                )
        except Exception as e:
            print(f"ML data yükleme hatası: {e}")

# Global instance
ml_learning = MLLearningSystem()
