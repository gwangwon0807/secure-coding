from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, blocks, categories, chat_rooms, community, images, items, reports, transactions, transfers, users


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(community.router, prefix="/community", tags=["community"])
api_router.include_router(chat_rooms.router, prefix="/chat-rooms", tags=["chat-rooms"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(transfers.router, prefix="/transfers", tags=["transfers"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(blocks.router, prefix="/blocks", tags=["blocks"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
