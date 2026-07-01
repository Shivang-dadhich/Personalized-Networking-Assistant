import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# Import your underlying service functions
from app.services.event_analyzer import extract_event_themes
from app.services.fact_checker import fact_check
from app.services.topic_generator import generate_topics
from app.services.history_logger import log_conversation

# Import your core global schemas
from app.models.schemas import EventContext, WikipediaFactCheck

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/conversation",
    tags=["Conversation & Orchestration"]
)

# ==========================================
# ENDPOINT LOCAL SCHEMAS (Request/Response)
# ==========================================

class AnalyzeEventRequest(BaseModel):
    event_description: str = Field(..., description="Raw text description of the networking event")
    candidate_labels: List[str] | None = Field(default=None, description="Optional custom categories to match against")

class FactCheckRequest(BaseModel):
    query: str = Field(..., description="Topic or terminology string to query on Wikipedia")

class GenerateConversationRequest(BaseModel):
    event_description: str = Field(..., description="Raw text description of the networking event")
    user_interests: List[str] = Field(..., description="List of professional topics or subjects the user likes")

class GenerateConversationResponse(BaseModel):
    extracted_themes: List[str] = Field(..., description="Top 3 themes calculated by the DistilBERT classifier")
    conversation_starters: List[str] = Field(..., description="Icebreaker items created by the GPT-2 engine")


# ==========================================
# ROUTER ENDPOINTS
# ==========================================

@router.post("/analyze-event", response_model=EventContext)
async def analyze_event_endpoint(payload: AnalyzeEventRequest):
    """
    Standalone endpoint to extract themes from an event description using the DistilBERT classifier.
    Useful for debugging or isolated testing.
    """
    try:
        themes = extract_event_themes(payload.event_description, payload.candidate_labels)
        
        # Mapping cleanly to your formal EventContext schema layout
        return EventContext(
            EventDescription=payload.event_description,
            AnalyzedThemes=themes
        )
    except Exception as e:
        logger.error(f"Router error in /analyze-event: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error during theme analysis.")


@router.post("/fact-check", response_model=WikipediaFactCheck)
async def fact_check_endpoint(payload: FactCheckRequest):
    """
    Wraps the Wikipedia verification service in an API contract.
    Returns structured data detailing the result of the lookups.
    """
    try:
        verification_result = fact_check(payload.query)
        
        # Map output to your formal Pydantic WikipediaFactCheck layout
        # (Using a mock or system ID placeholder 0 for session tracking context if unbound)
        return WikipediaFactCheck(
            SessionID=0, 
            VerifiedQueryText=payload.query,
            VerificationStatus=verification_result,
            WikipediaSourceURL=f"https://en.wikipedia.org/wiki/{payload.query.strip().replace(' ', '_')}"
        )
    except Exception as e:
        logger.error(f"Router error in /fact-check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing failure during fact-checking search.")


@router.post("/generate-conversation", response_model=GenerateConversationResponse)
async def generate_conversation_endpoint(payload: GenerateConversationRequest):
    """
    Primary orchestrator endpoint. 
    1. Extracts themes via event analyzer.
    2. Generates context-aware conversation topics via generator.
    3. Triggers automatic background side-effect history logging.
    """
    # Step 1: Run the Event Theme Extractor Pipeline
    try:
        themes = extract_event_themes(payload.event_description)
    except Exception as e:
        logger.error(f"Pipeline failed at extraction stage: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse event context parameters.")

    # Step 2: Generate the Conversation Icebreakers
    try:
        starters = generate_topics(extracted_themes=themes, user_interests=payload.user_interests)
    except Exception as e:
        logger.error(f"Pipeline failed at generation stage: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to construct generation dialogue context.")

    # Step 3: Automatic Side-Effect Logging (The frontend completely ignores this step)
    # The read-modify-write storage transaction occurs decoupled completely in the backend
    log_success = log_conversation(
        event_description=payload.event_description,
        extracted_themes=themes,
        conversation_starters=starters
    )
    
    if not log_success:
        logger.warning("Pipeline completed generation but failed background history persist verification.")

    # Step 4: Return response structured explicitly as requested
    return GenerateConversationResponse(
        extracted_themes=themes,
        conversation_starters=starters
    )
    
    
    
    
    
@router.get("/history", response_model=List[Dict[str, Any]])
async def get_history_endpoint():
    """
    Scenario 3 Requirement: Fetches all tracked historic logs 
    and interaction metrics from storage to review inside the UI.
    """
    try:
        # Assuming you have a fetch function inside your history_logger
        from app.services.history_logger import load_history
        logs = load_history()
        return logs
    except Exception as e:
        logger.error(f"Failed to fetch historical session array: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve session memory.")
    


class FeedbackRequest(BaseModel):
    suggestion_text: str
    is_useful: bool

@router.post("/feedback", status_code=status.HTTP_200_OK)
async def submit_feedback_endpoint(payload: FeedbackRequest):
    """
    Captures runtime feedback parameters (thumbs up loops) 
    to encourage optimization metrics.
    """
    try:
        from app.services.feedback_logger import log_feedback
        success = log_feedback(payload.suggestion_text, payload.is_useful)
        if not success:
            raise HTTPException(status_code=404, detail="Target suggestion text index context match missing.")
        return {"status": "Feedback logged successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit metrics transaction: {str(e)}")
    
    
@router.get("/feedback", response_model=List[Dict[str, Any]])
async def get_feedback_endpoint():
    """
    Retrieves all logged feedback entries for review and analysis.
    """
    try:
        from app.services.feedback_logger import load_feedback
        feedback_entries = load_feedback()
        return feedback_entries
    except Exception as e:
        logger.error(f"Failed to fetch feedback logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve feedback logs.")