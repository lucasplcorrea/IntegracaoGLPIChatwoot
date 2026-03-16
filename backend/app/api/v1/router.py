from fastapi import APIRouter

from app.api.v1.contacts import router as contacts_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.webhooks import router as webhooks_router

api_router = APIRouter()
api_router.include_router(webhooks_router)
api_router.include_router(contacts_router)
api_router.include_router(conversations_router)
