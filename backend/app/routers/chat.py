from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .. import models, database
from ..agent import run_agent, run_agent_stream
from ..tools import ShoppingTools
from ..utils.prompts import get_system_prompt
from ..limiter import limiter
import logging
import uuid
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)

# Concurrency Control: Max 5 concurrent chat requests processing
MAX_CONCURRENT_CHATS = 5
chat_semaphore = asyncio.Semaphore(MAX_CONCURRENT_CHATS)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: str = "default_session"
    cart: Optional[List[Dict[str, Any]]] = None

@router.post("/")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, chat_req: ChatRequest, db: Session = Depends(database.get_db)):
    """
    Chat endpoint with rate limiting (10/min) and concurrency control (max 5 simultaneous).
    """
    request_id = str(uuid.uuid4())
    logger.info(f"Received chat request [Req: {request_id}] Session: {chat_req.session_id}")
    
    try:
        # Sync cart if provided
        if chat_req.cart is not None:
            logger.info(f"Syncing cart for session {chat_req.session_id} with {len(chat_req.cart)} items")
            tools = ShoppingTools(db, chat_req.session_id)
            tools.sync_cart(chat_req.cart)

        # Convert messages to format expected by agent
        agent_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in chat_req.messages
        ]
        
        # Add a system message context from config
        system_prompt_config = get_system_prompt()
        if system_prompt_config:
            system_prompt = {
                "role": system_prompt_config.get("role", "system"),
                "content": system_prompt_config.get("content", "")
            }
            agent_messages.insert(0, system_prompt)
        
        # Concurrency controlled generator
        async def semaphore_wrapped_generator():
            async with chat_semaphore:
                async for chunk in run_agent_stream(agent_messages, db, chat_req.session_id, request_id):
                    yield chunk

        return StreamingResponse(
            semaphore_wrapped_generator(),
            media_type="text/plain"
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint [Req: {request_id}]: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
