import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import time

# Lazy imports to avoid startup bottleneck
import torch
from transformers import AutoTokenizer, AutoModelForMaskedLM, pipeline
from symspellpy import SymSpell, Verbosity
import pkg_resources

class NLPEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NLPEngine, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if self.initialized:
            return
            
        print("NLP Engine Initializing...")
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.models_dir = self.base_dir / "models" / "bert_tr"
        self.data_dir = self.base_dir / "data"
        
        # Components
        self.sym_spell = None
        self.fill_mask = None
        self.tokenizer = None
        self.model = None
        
        self.initialized = True

    async def load_models(self):
        """Async loader for heavy models"""
        if self.fill_mask and self.sym_spell:
            return

        print("Loading SymSpell...")
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        
        # Load Frequency Dictionary
        # We expect setup_ai.py to have created/downloaded "tr_frequencies.json" or a txt.
        # SymSpell needs a specific format (word count).
        # We will use the custom one we created.
        freq_path = self.data_dir / "tr_frequencies.json"
        
        # If we have JSON, we need to adapt since SymSpell usually reads text.
        # Or we can load directly from dictionary object.
        import json
        if freq_path.exists():
            with open(freq_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Create a temporary file for SymSpell load_dictionary
                # Or iterating and creating_dictionary_entry is slower.
                # Let's write a temp file.
                temp_dict = self.data_dir / "symspell_freq.txt"
                with open(temp_dict, 'w', encoding='utf-8') as tf:
                    for word, count in data.items():
                        tf.write(f"{word} {count}\n")
                
                self.sym_spell.load_dictionary(str(temp_dict), term_index=0, count_index=1, separator=" ")
                # os.remove(temp_dict) # Keep it for cache
        else:
            print("Warning: Frequency dictionary not found. Spell check will be empty.")

        print("Loading Transformer (BERT)...")
        # Load from local cache if available
        try:
            model_path = str(self.models_dir) if self.models_dir.exists() else "dbmdz/bert-base-turkish-cased"
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForMaskedLM.from_pretrained(model_path)
            
            device = 0 if torch.cuda.is_available() else -1
            self.fill_mask = pipeline("fill-mask", model=self.model, tokenizer=self.tokenizer, device=device)
        except Exception as e:
            print(f"Error loading BERT: {e}")

        print("NLP Engine Ready!")

    def correct_spelling(self, text: str) -> List[Dict]:
        """
        Fast spell checking using SymSpell.
        Returns suggestions with confidence scores.
        """
        if not self.sym_spell:
            return []
            
        suggestions = self.sym_spell.lookup(text, Verbosity.CLOSEST, max_edit_distance=2)
        results = []
        for sug in suggestions:
            results.append({
                "word": sug.term,
                "distance": sug.distance,
                "count": sug.count
            })
        return results

    def predict_next(self, context: str) -> List[str]:
        """
        Predicts completion using BERT Masked LM.
        BERT isn't a generative model like GPT, but it's great for 'filling in the blanks'.
        For true 'next word prediction', GPT-2 Turkish would be better, but BERT is robust for general context. 
        We can cheat by appending a [MASK] token.
        """
        if not self.fill_mask:
            return []

        # Simple approach: Context + [MASK]
        # "Bugün hava çok [MASK]" -> güzel, soğuk, sıcak...
        masked_text = f"{context} [MASK]"
        try:
            results = self.fill_mask(masked_text)
            return [res['token_str'] for res in results]
        except:
            return []

    def analyze_sentiment(self, text: str) -> str:
        # Placeholder for sentiment
        return "neutral"

nlp_engine = NLPEngine()
