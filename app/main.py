from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.networking import router as networking_router


def create_app() -> FastAPI:
	app = FastAPI(title=settings.app_name, version="0.1.0")
	app.add_middleware(
		CORSMiddleware,
		allow_origins=list(settings.allow_origins),
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)
	app.include_router(networking_router)
	return app


app = create_app()

