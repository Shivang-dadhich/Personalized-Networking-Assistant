from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class _SchemaBase(BaseModel):
	model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)


class UserProfile(_SchemaBase):
	user_id: int | None = Field(default=None, alias="UserID", description="Primary key for the user profile")
	bio_text: str = Field(..., alias="BioText", description="Persistent biography or profile summary for the user")
	current_event_cache: dict[str, Any] | None = Field(
		default=None,
		alias="currentEventCache",
		description="Cached event-specific data associated with the user",
	)


class EventContext(_SchemaBase):
	event_id: int | None = Field(default=None, alias="EventID", description="Primary key for the event context")
	event_description: str = Field(
		..., alias="EventDescription", description="Text description of the event or networking context"
	)
	analyzed_themes: list[str] = Field(
		default_factory=list,
		alias="AnalyzedThemes",
		description="Themes extracted from the event description or related context",
	)


class NetworkingSession(_SchemaBase):
	session_id: int | None = Field(default=None, alias="SessionID", description="Primary key for the networking session")
	user_id: int = Field(..., alias="UserID", description="Foreign key referencing the user profile")
	event_id: int = Field(..., alias="EventID", description="Foreign key referencing the event context")
	session_timestamp: datetime = Field(
		default_factory=datetime.utcnow,
		alias="SessionTimestamp",
		description="Timestamp when the networking session was created",
	)


class GeneratedStarter(_SchemaBase):
	starter_id: int | None = Field(default=None, alias="StarterID", description="Primary key for the generated starter")
	session_id: int = Field(..., alias="SessionID", description="Foreign key referencing the networking session")
	starter_text: str = Field(..., alias="StarterText", description="AI-generated conversation starter text")
	context_prompt_used: str = Field(
		..., alias="ContextPromptUsed", description="Prompt or context that produced the starter"
	)


class WikipediaFactCheck(_SchemaBase):
	fact_check_id: int | None = Field(
		default=None, alias="FactCheckID", description="Primary key for the Wikipedia fact-check record"
	)
	session_id: int = Field(..., alias="SessionID", description="Foreign key referencing the networking session")
	verified_query_text: str = Field(
		..., alias="VerifiedQueryText", description="Query text verified against Wikipedia or related sources"
	)
	verification_status: str = Field(..., alias="VerificationStatus", description="Result of the verification attempt")
	wikipedia_source_url: str | None = Field(
		default=None,
		alias="WikipediaSourceURL",
		description="Source URL used to verify the query, if available",
	)


class LogEntry(_SchemaBase):
	log_id: int | None = Field(default=None, alias="LogID", description="Primary key for the audit log entry")
	session_id: int | None = Field(
		default=None,
		alias="SessionID",
		description="Optional foreign key referencing the networking session",
	)
	action_type: str = Field(..., alias="ActionType", description="Type of action that triggered the log entry")
	payload_json: dict[str, Any] = Field(..., alias="PayloadJSON", description="Structured payload captured for auditing")
	timestamp: datetime = Field(default_factory=datetime.utcnow, alias="Timestamp", description="Log creation timestamp")


__all__ = [
	"UserProfile",
	"EventContext",
	"NetworkingSession",
	"GeneratedStarter",
	"WikipediaFactCheck",
	"LogEntry",
]
