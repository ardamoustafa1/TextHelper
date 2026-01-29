from fastapi import APIRouter, HTTPException, Depends, WebSocket
from app.api.schemas import ProcessRequest, ResponseModel, SuggestionItem
from app.core.nlp_engine import NLPEngine, nlp_engine
from app.core.cache import cache_manager
import time

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            start_time = time.time()
            data = await websocket.receive_json()
            # print(f"[WS DEBUG] Received: {data}") # Uncomment for full noise
            text = data.get("text", "")
            print(f"[WS DEBUG] Processing text: '{text}'")
            
            suggestions = []
            
            # 1. Prefix Completion
            words = text.strip().split()
            if words:
                last_word = words[-1]
                prefix_results = nlp_engine.complete_prefix(last_word, max_results=5)
                for res in prefix_results:
                    if res['word'].lower() != last_word.lower():
                        # Score calculation: Base 10 + frequency boost
                        raw_count = res.get('count', 0)
                        score_val = 10.0 + (min(raw_count, 1000) / 100.0) 
                        
                        suggestions.append({
                            "text": res['word'],
                            "confidence": 1.0, 
                            "type": 'completion',
                            "score": score_val,
                            "source": res.get('source', 'unknown'),
                            "description": "Tamamlama"
                        })
            
            # 2. Next Word (Hybrid)
            predictions = nlp_engine.predict_next(text)
            for pred in predictions[:3]:
                suggestions.append({
                     "text": pred['word'],
                     "confidence": pred['score'],
                     "type": 'next_word',
                     "score": pred['score'] * 10, # ~9.0 range
                     "source": pred['source'],
                     "description": "Tahmin"
                })

            print(f"[WS DEBUG] Sending {len(suggestions)} suggestions")
            process_time = (time.time() - start_time) * 1000
            await websocket.send_json({
                "suggestions": suggestions,
                "processing_time_ms": process_time
            })

    except Exception as e:
        print(f"WebSocket Error: {e}")
        pass

async def get_engine():
    if not nlp_engine.initialized:
        await nlp_engine.load_models()
    return nlp_engine

@router.post("/process", response_model=ResponseModel)
async def process_text(request: ProcessRequest, engine: NLPEngine = Depends(get_engine)):
    """
    Main endpoint for text processing.
    """
    start_time = time.time()
    
    # 0. Check Cache
    cache_key = f"process:{request.text}:{request.context or ''}"
    cached_response = cache_manager.get(cache_key)
    if cached_response:
        return ResponseModel(**cached_response)

    suggestions = []
    print(f"[HTTP DEBUG] Processing request: '{request.text}'")
    
    words = request.text.strip().split()
    if not words:
        return ResponseModel(original=request.text, suggestions=[])
        
    last_word = words[-1]
    
    # 1. PREFIX COMPLETION
    prefix_results = engine.complete_prefix(last_word, max_results=5)
    for res in prefix_results:
        if res['word'].lower() != last_word.lower():
            raw_count = res.get('count', 0)
            score_val = 10.0 + (min(raw_count, 1000) / 100.0)
            
            suggestions.append(SuggestionItem(
                text=res['word'],
                confidence=1.0, 
                type='completion',
                score=score_val,
                source=res.get('source', 'unknown'),
                description="Tamamlama"
            ))
        
    # 2. GPT-2 Generation
    context_str = request.text
    if len(context_str.strip()) > 2:
        generations = engine.generate_text(context_str, max_new_tokens=4)
        for gen in generations:
            if len(gen) > len(context_str):
                clean_gen = gen[len(context_str):].strip()
                if clean_gen:
                    suggestions.append(SuggestionItem(
                        text=clean_gen,
                        confidence=0.85,
                        type='ai_generation',
                        score=8.0,
                        source="gpt2",
                        description="AI"
                    ))
    
    # 3. Hybrid Prediction (Next Word)
    predictions = engine.predict_next(context_str)
    existing_texts = {s.text for s in suggestions}
    
    for pred in predictions[:3]: 
        if pred['word'] not in existing_texts:
             suggestions.append(SuggestionItem(
                text=pred['word'],
                confidence=pred['score'],
                type='next_word',
                score=pred['score'] * 10,
                source=pred.get('source', 'bert'),
                description="Tahmin"
            ))
            
    # Sort suggestions by score descending
    suggestions.sort(key=lambda x: x.score, reverse=True)
            
    process_time = (time.time() - start_time) * 1000
    
    final_response = ResponseModel(
        original=request.text,
        suggestions=suggestions,
        sentiment="neutral",
        processing_time_ms=process_time
    )
    
    # Cache
    cache_manager.set(cache_key, final_response.model_dump(), ttl=3600)
    
    print(f"[HTTP DEBUG] Returning {len(suggestions)} suggestions")
    return final_response

@router.post("/learn")
async def learn_feedback(feedback: dict):
    try:
        text = feedback.get('text')
        if text:
            nlp_engine.learn(text)
        return {"status": "success"}
    except Exception as e:
        print(f"[LEARN] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    from app.core.search_service import search_service
    return {
        "status": "active", 
        "transformer_loaded": nlp_engine.initialized,
        "elasticsearch_available": search_service.available
    }
