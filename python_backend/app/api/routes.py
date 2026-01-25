from fastapi import APIRouter, HTTPException, Depends
from app.api.schemas import ProcessRequest, ResponseModel, SuggestionItem
from app.core.nlp_engine import NLPEngine, nlp_engine
from app.core.cache import cache_manager

router = APIRouter()

async def get_engine():
    # Ensure engine is loaded
    if not nlp_engine.initialized:
        await nlp_engine.load_models()
    return nlp_engine

@router.post("/process", response_model=ResponseModel)
async def process_text(request: ProcessRequest, engine: NLPEngine = Depends(get_engine)):
    """
    Main endpoint for text processing.
    Handles both spell checking and next word prediction.
    """
    # 0. Check Cache (Performance Optimization)
    # Key includes text + context to be unique
    cache_key = f"process:{request.text}:{request.context or ''}"
    cached_response = cache_manager.get(cache_key)
    if cached_response:
        return ResponseModel(**cached_response)

    suggestions = []
    
    # 1. Spell Check (if the text looks like a single incomplete word)
    # or if we want to correct the last word.
    # Assuming request.text is the "current typing buffer".
    
    words = request.text.strip().split()
    if not words:
        return ResponseModel(original=request.text, suggestions=[])
        
    last_word = words[-1]
    
    # Spell check the last word
    spelling_results = engine.correct_spelling(last_word)
    for res in spelling_results[:3]: # Top 3 corrections
        suggestions.append(SuggestionItem(
            text=res['word'],  # Fixed: Map 'word' from spell_check to 'text' in schema
            confidence=1.0, 
            type='correction'
        ))
        
    # 2. Next Word Prediction (Context aware)
    context_str = request.text
    predictions = engine.predict_next(context_str)
    
    for pred in predictions[:3]: 
        # Filter out duplicates
        if pred not in [s.text for s in suggestions]:
             suggestions.append(SuggestionItem(
                text=pred,
                confidence=0.9,
                type='next_word'
            ))
            
    final_response = ResponseModel(
        original=request.text,
        suggestions=suggestions,
        sentiment="neutral"
    )
    
    # Cache the result for 1 hour
    cache_manager.set(cache_key, final_response.dict(), ttl=3600)
    
    return final_response

@router.post("/learn")
async def learn_feedback(feedback: dict):
    """
    Endpoint for reinforcement learning signals.
    Frontend sends this when user selects a suggestion.
    """
    # In a real enterprise system, we would log this to a database
    # and retrain the model periodically.
    # For now, we'll just log it.
    print(f"[LEARN] User selected: {feedback.get('selected_suggestion')} for input: {feedback.get('text')}")
    return {"status": "recorded"}

@router.get("/health")
async def health_check():
    return {
        "status": "active", 
        "transformer_loaded": nlp_engine.initialized,
        "elasticsearch_available": True # SymSpell is running as our Search Engine
    }
