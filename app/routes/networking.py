from fastapi import APIRouter, Query

from app.models.schema import (
	FactCheckRequest,
	FactCheckResponse,
	FeedbackRequest,
	FeedbackResponse,
	HealthResponse,
	HistoryResponse,
	StarterGenerationRequest,
	StarterGenerationResponse,
)

router = APIRouter(prefix="/api/networking", tags=["networking"])


@router.get("/health", response_model=HealthResponse)
def health_check():
	return HealthResponse(status="ok")


@router.post("/starters", response_model=StarterGenerationResponse)
def generate_starters(payload: StarterGenerationRequest):
	return StarterGenerationResponse(
		session_id=1,
		event_description=payload.event_description,
		interests=payload.interests,
		themes=["AI", "Sustainability"],
		conversation_starters=[
			"What are your thoughts on implementing AI for sustainable cities?",
			"How do you see urban planning evolving with AI technologies?",
		],
	)


@router.post("/fact-check", response_model=FactCheckResponse)
def fact_check(payload: FactCheckRequest):
	return FactCheckResponse(
		query_text=payload.query_text,
		verification_status="verified",
		summary="Sample fact check summary from Wikipedia",
		wikipedia_source_url="https://en.wikipedia.org/wiki/Sample",
	)


@router.get("/history", response_model=HistoryResponse)
def history(user_id: int | None = Query(default=None)):
	return HistoryResponse(items=[])


@router.post("/feedback", response_model=FeedbackResponse)
def feedback(payload: FeedbackRequest):
	return FeedbackResponse(success=True, message="Feedback logged")
