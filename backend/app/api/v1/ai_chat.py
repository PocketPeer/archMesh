"""
AI Chat API endpoints for real-time AI assistance and model switching
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import json
import logging

from app.services.ai_chat_service import AIChatService
from app.core.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-chat", tags=["ai-chat"])


class ChatMessage(BaseModel):
    """Chat message model"""
    id: str = Field(..., description="Unique message ID")
    content: str = Field(..., description="Message content")
    role: str = Field(..., description="Message role: user, assistant, system")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_used: Optional[str] = Field(None, description="AI model used for this message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ChatSession(BaseModel):
    """Chat session model"""
    id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Session title")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[ChatMessage] = Field(default_factory=list)
    current_model: str = Field(default="deepseek-r1", description="Currently selected model")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SendMessageRequest(BaseModel):
    """Request to send a message"""
    content: str = Field(..., description="Message content")
    session_id: Optional[str] = Field(None, description="Session ID (creates new if not provided)")
    model: Optional[str] = Field(None, description="AI model to use")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SendMessageResponse(BaseModel):
    """Response from sending a message"""
    success: bool
    message: ChatMessage
    session_id: str
    model_used: str
    error: Optional[str] = None


class AvailableModelsResponse(BaseModel):
    """Available AI models"""
    models: List[Dict[str, Any]]
    current_model: str
    default_model: str


class SwitchModelRequest(BaseModel):
    """Request body for switching model"""
    model: str = Field(..., description="AI model key to switch to")


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
    
    async def connect(self, websocket: WebSocket, user_id: str, session_id: str):
        """Connect a user to a chat session"""
        await websocket.accept()
        connection_key = f"{user_id}:{session_id}"
        self.active_connections[connection_key] = websocket
        self.user_sessions[user_id] = session_id
        logger.info(f"User {user_id} connected to session {session_id}")
    
    def disconnect(self, user_id: str, session_id: str):
        """Disconnect a user from a chat session"""
        connection_key = f"{user_id}:{session_id}"
        if connection_key in self.active_connections:
            del self.active_connections[connection_key]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        logger.info(f"User {user_id} disconnected from session {session_id}")
    
    async def send_message(self, user_id: str, session_id: str, message: dict):
        """Send a message to a specific user session"""
        connection_key = f"{user_id}:{session_id}"
        if connection_key in self.active_connections:
            websocket = self.active_connections[connection_key]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_key}: {e}")
                self.disconnect(user_id, session_id)
    
    async def broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast a message to all users in a session"""
        for connection_key, websocket in self.active_connections.items():
            if connection_key.endswith(f":{session_id}"):
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_key}: {e}")


# Global connection manager
manager = ConnectionManager()


@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models(current_user: User = Depends(get_current_user)):
    """Get available AI models for chat"""
    try:
        ai_chat_service = AIChatService()
        models = await ai_chat_service.get_available_models()
        current_model = await ai_chat_service.get_current_model()
        default_model = await ai_chat_service.get_default_model()
        
        return AvailableModelsResponse(
            models=models,
            current_model=current_model,
            default_model=default_model
        )
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available models")


@router.post("/sessions", response_model=ChatSession)
async def create_chat_session(
    title: str = "New Chat Session",
    current_user: User = Depends(get_current_user)
):
    """Create a new chat session"""
    try:
        ai_chat_service = AIChatService()
        session = await ai_chat_service.create_session(
            user_id=str(current_user.id),
            title=title
        )
        return session
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chat session")


@router.get("/sessions", response_model=List[ChatSession])
async def get_user_sessions(current_user: User = Depends(get_current_user)):
    """Get all chat sessions for the current user"""
    try:
        ai_chat_service = AIChatService()
        sessions = await ai_chat_service.get_user_sessions(str(current_user.id))
        return sessions
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat sessions")


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific chat session"""
    try:
        ai_chat_service = AIChatService()
        session = await ai_chat_service.get_session(session_id, str(current_user.id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat session")


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """Send a message to a chat session"""
    try:
        ai_chat_service = AIChatService()
        
        # Verify session ownership
        session = await ai_chat_service.get_session(session_id, str(current_user.id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Send message
        response = await ai_chat_service.send_message(
            session_id=session_id,
            user_id=str(current_user.id),
            content=request.content,
            model=request.model,
            context=request.context
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.put("/sessions/{session_id}/model")
async def switch_model(
    session_id: str,
    request: Optional[SwitchModelRequest] = None,
    model: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Switch the AI model for a chat session"""
    try:
        ai_chat_service = AIChatService()
        
        # Verify session ownership
        session = await ai_chat_service.get_session(session_id, str(current_user.id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Accept model from JSON body or query param
        target_model = (request.model if request else None) or model
        if not target_model:
            raise HTTPException(status_code=422, detail="Model is required")

        # Switch model
        success = await ai_chat_service.switch_model(session_id, target_model)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid model or failed to switch")
        
        return {"success": True, "model": target_model}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching model: {e}")
        raise HTTPException(status_code=500, detail="Failed to switch model")


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a chat session"""
    try:
        ai_chat_service = AIChatService()
        
        # Verify session ownership
        session = await ai_chat_service.get_session(session_id, str(current_user.id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete session
        success = await ai_chat_service.delete_session(session_id, str(current_user.id))
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete session")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, str(current_user.id), session_id)
    
    try:
        ai_chat_service = AIChatService()
        
        # Verify session ownership
        session = await ai_chat_service.get_session(session_id, str(current_user.id))
        if not session:
            await websocket.close(code=1008, reason="Session not found")
            return
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                # Process the message
                content = message_data.get("content", "")
                model = message_data.get("model")
                context = message_data.get("context", {})
                
                # Send user message immediately
                user_message = {
                    "type": "user_message",
                    "content": content,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.send_message(str(current_user.id), session_id, user_message)
                
                # Generate AI response
                try:
                    response = await ai_chat_service.send_message(
                        session_id=session_id,
                        user_id=str(current_user.id),
                        content=content,
                        model=model,
                        context=context
                    )
                    
                    # Send AI response
                    ai_message = {
                        "type": "ai_message",
                        "content": response.message.content,
                        "model_used": response.model_used,
                        "timestamp": response.message.timestamp.isoformat(),
                        "metadata": response.message.metadata
                    }
                    await manager.send_message(str(current_user.id), session_id, ai_message)
                    
                except Exception as e:
                    logger.error(f"Error generating AI response: {e}")
                    error_message = {
                        "type": "error",
                        "content": f"Sorry, I encountered an error: {str(e)}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await manager.send_message(str(current_user.id), session_id, error_message)
            
            elif message_data.get("type") == "ping":
                # Respond to ping with pong
                pong_message = {
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.send_message(str(current_user.id), session_id, pong_message)
    
    except WebSocketDisconnect:
        manager.disconnect(str(current_user.id), session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(str(current_user.id), session_id)
        await websocket.close(code=1011, reason="Internal server error")

