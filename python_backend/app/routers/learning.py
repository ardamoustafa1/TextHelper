from fastapi import APIRouter, BackgroundTasks
from app.models.schemas import FeedbackRequest
from app.core.logs import logger
from app.core.telemetry import telemetry

# Optional Learning Modules
try:
    from app.features.ml_learning import ml_learning
    ML_LEARNING_AVAILABLE = True
except ImportError:
    ML_LEARNING_AVAILABLE = False
    ml_learning = None

try:
    from app.features.advanced_ngram import advanced_ngram
    ADVANCED_NGRAM_AVAILABLE = True
except ImportError:
    ADVANCED_NGRAM_AVAILABLE = False
    advanced_ngram = None

try:
    from app.features.advanced_ranking import advanced_ranking
    ADVANCED_RANKING_AVAILABLE = True
except ImportError:
    ADVANCED_RANKING_AVAILABLE = False
    advanced_ranking = None

try:
    from app.features.ml_ranking import ml_ranking
    ML_RANKING_AVAILABLE = True
except ImportError:
    ML_RANKING_AVAILABLE = False
    ml_ranking = None


router = APIRouter()


def background_learn(user_id: str, text: str, selected_suggestion: str):
    """Arka planda öğrenme işlemi (ML + N-gram + Ranking)."""
    # 1. ML Learning (kullanıcı davranışı → Redis / lokal)
    if ML_LEARNING_AVAILABLE and ml_learning:
        try:
            ml_learning.learn_from_interaction(user_id, text, selected_suggestion)
            logger.info(f"[LEARN] ML learning: user={user_id}")
        except Exception as e:
            logger.error(f"Background ML learning hatası: {e}")

    # 2. N-gram Learning
    if ADVANCED_NGRAM_AVAILABLE and advanced_ngram and hasattr(
        advanced_ngram, "learn_from_text"
    ):
        try:
            advanced_ngram.learn_from_text(text)
            if selected_suggestion:
                full_text = f"{text} {selected_suggestion}"
                advanced_ngram.learn_from_text(full_text)
            logger.info(f"[LEARN] N-gram learning completed")
        except Exception as e:
            logger.error(f"Background N-gram learning hatası: {e}")

    # 3. Gelişmiş Ranking (CTR bazlı)
    if ADVANCED_RANKING_AVAILABLE and advanced_ranking and selected_suggestion and hasattr(
        advanced_ranking, "record_click"
    ):
        try:
            advanced_ranking.record_click(selected_suggestion)
            logger.info(f"[LEARN] Advanced ranking click recorded")
        except Exception as e:
            logger.error(f"Background advanced ranking hatası: {e}")

    # 4. ML Ranking System (kullanıcı seçimlerine göre skorlama)
    if ML_RANKING_AVAILABLE and ml_ranking and selected_suggestion:
        try:
            context = {"text": text}
            ml_ranking.learn_from_selection(user_id, selected_suggestion, context)
            logger.info(f"[LEARN] ML ranking selection recorded")
        except Exception as e:
            logger.error(f"Background ML ranking hatası: {e}")

    # 5. Telemetry: accept event
    try:
        telemetry.record_accept(user_id, text, selected_suggestion, source="unknown")
    except Exception:
        pass


@router.post("/learn")
async def learn_interaction(feedback: FeedbackRequest, background_tasks: BackgroundTasks):
    """Kullanıcı etkileşiminden öğren (fire-and-forget)."""
    background_tasks.add_task(
        background_learn,
        feedback.user_id,
        feedback.text,
        feedback.selected_suggestion,
    )
    return {"status": "queued"}
