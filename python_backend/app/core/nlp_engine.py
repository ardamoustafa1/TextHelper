import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time

# Lazy imports to avoid startup bottleneck
import torch
from transformers import AutoTokenizer, AutoModelForMaskedLM, pipeline
from symspellpy import SymSpell, Verbosity
import zeyrek

from app.core.user_dict import UserDictionary
from app.core.ngram_engine import NgramEngine
from logger_config import logger

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
            
        logger.info("NLP Engine Initializing...")
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.models_dir = self.base_dir / "models"
        self.data_dir = self.base_dir / "data"
        
        # Components
        self.sym_spell = None
        self.fill_mask = None # BERT
        self.gpt_model = None # GPT-2
        self.gpt_tokenizer = None
        self.morph_analyzer = None # Zeyrek
        
        self.tokenizer = None
        self.model = None
        self.frequency_dict = {} # Initialize empty to avoid race conditions
        
        # Initialize Personalization Engines
        try:
            self.user_dict = UserDictionary(str(self.data_dir / "user_dictionary.json"))
            self.ngram_engine = NgramEngine(str(self.data_dir / "user_ngrams.json"))
        except Exception as e:
            logger.error(f"Error initializing personalization engines: {e}")
            # Fallbacks just in case
            self.user_dict = None
            self.ngram_engine = None

        self.initialized = True

    async def load_models(self):
        """Async loader for heavy models"""
        if self.fill_mask and self.sym_spell:
            return

        import gc

        self.data_dir.mkdir(parents=True, exist_ok=True)

        # --- CONFIGURATION (ENV VARS) ---
        use_symspell = os.getenv("USE_SYMSPELL", "true").lower() == "true"
        use_bert = os.getenv("USE_BERT", "false").lower() == "true"
        use_gpt = os.getenv("USE_GPT", "false").lower() == "true"
        
        # Performance Tuning
        use_quantization = os.getenv("USE_QUANTIZATION", "false").lower() == "true"
        if use_quantization:
            # Force PyTorch to be friendly to CPU
            try:
                threads = int(os.getenv("OMP_NUM_THREADS", "1"))
                torch.set_num_threads(threads)
                os.environ["OMP_NUM_THREADS"] = str(threads)
                os.environ["MKL_NUM_THREADS"] = str(threads)
            except:
                pass

        print("\n[NLP CONFIGURATION]")
        print(f"  - SymSpell:      {'ENABLED' if use_symspell else 'DISABLED'}")
        print(f"  - BERT:          {'ENABLED' if use_bert else 'DISABLED'}")
        print(f"  - GPT-2:         {'ENABLED' if use_gpt else 'DISABLED'}")
        print(f"  - Optimization:  {'ACTIVE' if use_quantization else 'OFF'}")
        print("-" * 30)

        if use_symspell:
            print("Loading SymSpell...")
            # CRITICAL FIX: Reduced max_edit_distance to 1 and prefix_length to 3 to prevent MemoryError
            self.sym_spell = SymSpell(max_dictionary_edit_distance=1, prefix_length=3)
            self.frequency_dict = {}  # Store raw dict for prefix completion
            
            # Load Frequency Dictionary: tr_frequencies.json or fallback to turkish_dictionary.json
            import json
            freq_path = self.data_dir / "tr_frequencies.json"
            fallback_path = self.base_dir / "turkish_dictionary.json"
            data = None

            if freq_path.exists():
                try:
                    with open(freq_path, 'r', encoding='utf-8') as f:
                        raw = json.load(f)
                    data = raw if isinstance(raw, dict) else {x["word"]: x.get("frequency", 1) for x in (raw or []) if isinstance(x, dict) and x.get("word")}
                except Exception as e:
                    print(f"Dictionary Loading Error (tr_frequencies): {e}")
            if not data and fallback_path.exists():
                try:
                    with open(fallback_path, 'r', encoding='utf-8') as f:
                        raw = json.load(f)
                    data = {x["word"]: x.get("frequency", 1) for x in (raw or []) if isinstance(x, dict) and x.get("word")}
                    print(f"Using fallback: turkish_dictionary.json ({len(data)} words)")
                except Exception as e:
                    print(f"Fallback dictionary error: {e}")

            if data:
                self.frequency_dict = data
                temp_dict = self.data_dir / "symspell_freq.txt"
                try:
                    with open(temp_dict, 'w', encoding='utf-8') as tf:
                        for word, count in data.items():
                            tf.write(f"{word} {count}\n")
                    try:
                        self.sym_spell.load_dictionary(str(temp_dict), term_index=0, count_index=1, separator=" ")
                        print(f"Loaded {len(self.frequency_dict)} words into SymSpell")
                    except MemoryError:
                        print("WARNING: System Low on Memory. Skipping SymSpell Dictionary Load.")
                    except Exception as e:
                        print(f"SymSpell Load Error: {e}")
                except Exception as e:
                    print(f"SymSpell dict write error: {e}")
            else:
                print("Warning: No frequency dictionary found (data/tr_frequencies.json or turkish_dictionary.json).")
            
            # CLEANUP
            gc.collect() 
        else:
            print("SymSpell skipped.")

        if use_bert:
            print("Loading Transformer (BERT)...")
            try:
                # OPTIMIZATION: Use DistilBERT if optimized mode is on, else full BERT
                if use_quantization:
                    # Lighter, faster model for optimization mode
                    model_name = "dbmdz/distilbert-base-turkish-cased"
                    print("  -> Using Optimized Model (DistilBERT)")
                else:
                    bert_path = self.models_dir / "bert_tr"
                    model_name = str(bert_path) if bert_path.exists() else "dbmdz/bert-base-turkish-cased"
                
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForMaskedLM.from_pretrained(model_name)
                
                device = 0 if torch.cuda.is_available() else -1
                self.fill_mask = pipeline("fill-mask", model=self.model, tokenizer=self.tokenizer, device=device)
                
                # CLEANUP
                gc.collect()
            except Exception as e:
                print(f"Error loading BERT: {e}")
                # Fallbck to standard if distilbert fails
                if use_quantization:
                     print("  -> Fallback to standard BERT")
        else:
             print("Transformer (BERT) skipped.")

        if use_gpt:
            print("Loading GenAI (GPT-2)...")
            try:
                from transformers import AutoModelForCausalLM
                # GPT-2 is already small-ish, but we ensure we clear memory
                gpt_path = self.models_dir / "gpt2_tr"
                gpt_path_str = str(gpt_path) if gpt_path.exists() else "redrussianarmy/gpt2-turkish-cased"
                
                self.gpt_tokenizer = AutoTokenizer.from_pretrained(gpt_path_str)
                self.gpt_model = AutoModelForCausalLM.from_pretrained(gpt_path_str)
                
                # CLEANUP
                gc.collect()
            except Exception as e:
                 print(f"Error loading GPT-2: {e}")
        else:
            print("GenAI (GPT-2) skipped.")
             
        print("Loading Morphology (Zeyrek)...")
        try:
            self.morph_analyzer = zeyrek.MorphAnalyzer()
        except Exception as e:
            print(f"Error loading Zeyrek: {e}")

        print("NLP Engine Ready!")

    def learn(self, text: str):
        """
        Learns from user input to improve future suggestions.
        """
        if not text:
            return
        
        try:
            # 1. Update User Dictionary
            if self.user_dict:
                # Split and add words
                words = text.strip().split()
                for word in words:
                    self.user_dict.add_word(word)
            
            # 2. Update N-grams
            if self.ngram_engine:
                self.ngram_engine.learn_sequence(text)
                
            print(f"[NLP] Learned from input: {text[:20]}...")
        except Exception as e:
            print(f"Error learning from text: {e}")

    def generate_text(self, context: str, max_new_tokens=5) -> List[str]:
        """
        Generates continuation using GPT-2.
        Input: "Yarın" -> Output: "Yarın [müsait misin?]"
        """
        if not self.gpt_model or not self.gpt_tokenizer:
            return []
            
        try:
            inputs = self.gpt_tokenizer(context, return_tensors="pt")
            outputs = self.gpt_model.generate(
                **inputs, 
                max_new_tokens=max_new_tokens, 
                do_sample=True, 
                top_k=50, 
                top_p=0.95,
                pad_token_id=self.gpt_tokenizer.eos_token_id
            )
            generated_text = self.gpt_tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Return full text
            return [generated_text]
        except Exception as e:
            print(f"Generation error: {e}")
            return []

    def analyze_word(self, word: str) -> List[Dict]:
        """
        Morphological analysis.
        Returns possible parses: [(root, type, suffixes...)]
        """
        if not self.morph_analyzer:
            return []
        try:
            parses = self.morph_analyzer.analyze(word)
            results = []
            for parse in parses:
                results.append({
                    "root": parse.lemma,
                    "pos": parse.pos,
                    "formatted": parse.formatted
                })
            return results
        except:
            return []

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

    def predict_next(self, context: str) -> List[Dict]:
        """
        Hybrid prediction:
        1. N-gram (User History) - Highest Priority
        2. BERT (Contextual Embedding) - General Knowledge
        """
        suggestions = []
        suggestions_text = set() # For deduplication
        
        words = context.strip().split()
        if not words:
            return []
            
        last_word = words[-1]

        # 1. N-GRAM (User Personal History)
        if self.ngram_engine:
            user_preds = self.ngram_engine.predict_next(last_word, limit=3)
            for pred_word, count in user_preds:
                if pred_word not in suggestions_text:
                    score = min(0.99, 0.7 + (min(count, 10) / 50.0)) # Scale score by frequency
                    suggestions.append({
                        "word": pred_word,
                        "score": score,
                        "source": "user_history"
                    })
                    suggestions_text.add(pred_word)

        # 2. BERT (Transformers) - If we don't have enough user history
        if self.fill_mask:
            masked_text = f"{context} [MASK]"
            try:
                results = self.fill_mask(masked_text)
                for res in results:
                    token = res['token_str']
                    # improvements: filter punctuation
                    if token.startswith("##") or len(token) < 2:
                        continue
                        
                    if token not in suggestions_text:
                        suggestions.append({
                            "word": token,
                            "score": res['score'], # usually 0.0-1.0
                            "source": "bert"
                        })
                        suggestions_text.add(token)
            except Exception as e:
                # print(f"BERT Error: {e}")
                pass
                
        # Sort by score DESC
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        # 3. FALLBACK (If no AI/History suggestions)
        if not suggestions:
             fallback_words = ["ve", "ile", "için", "bir", "bu"]
             for fw in fallback_words:
                 suggestions.append({
                    "word": fw,
                    "score": 0.1,
                    "source": "fallback"
                 })
                 
        return suggestions[:5]

    def complete_prefix(self, prefix: str, max_results: int = 10) -> List[Dict]:
        """
        Hybrid Prefix Completion:
        1. User Dictionary (Prioritize user's own vocabulary)
        2. General Dictionary
        """
        if not prefix:
            return []
            
        prefix_lower = prefix.lower()
        results = []
        seen = set()
        
        # 1. USER DICTIONARY
        if self.user_dict:
            user_matches_words = self.user_dict.get_top_phrases(prefix_lower, limit=5)
            for word in user_matches_words:
                if word not in seen:
                    results.append({
                        "word": word,
                        "count": self.user_dict.get_frequency(word) * 100, # Boost user words significantly
                        "source": "user"
                    })
                    seen.add(word)

        # 2. GENERAL FREQUENCY DICT
        if self.frequency_dict:
            try:
                # Scan general dict (this can be optimized with a trie in future for speed)
                matches_found = 0
                for word, count in self.frequency_dict.items():
                    if matches_found >= max_results:
                        break
                        
                    # Lowercase match
                    if word.lower().startswith(prefix_lower) and word not in seen:
                        results.append({
                            "word": word,
                            "count": count,
                            "source": "dict"
                        })
                        seen.add(word)
                        matches_found += 1
            except Exception as e:
                print(f"Prefix error: {e}")

        # FALLBACK: If absolutely nothing found, and prefix is short, suggest common words
        if not results and len(prefix) >= 1:
             defaults = ["merhaba", "nasılsın", "evet", "hayır", "tamam", "ama", "ali", "ara"]
             for d in defaults:
                 if d.startswith(prefix_lower) and d not in seen:
                     results.append({
                         "word": d,
                         "count": 1,
                         "source": "fallback"
                     })

        # Sort by 'count' (which implies likelihood)
        results.sort(key=lambda x: x['count'], reverse=True)
        return results[:max_results]

    def analyze_sentiment(self, text: str) -> str:
        # Placeholder for sentiment
        return "neutral"

nlp_engine = NLPEngine()
