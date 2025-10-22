"""
AI Chat Service for ArchMesh
TDD Implementation - RED phase: Define interfaces and create failing tests first
"""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json

from app.core.llm_strategy import LLMStrategy, TaskType
from app.config import settings
import httpx
from app.core.logging_config import get_logger
from app.core.exceptions import AIChatError, ValidationError

logger = get_logger(__name__)

# Module-level stores so sessions persist across service instances (per process)
_SESSIONS: Dict[str, Dict[str, Any]] = {}
_USER_SESSIONS: Dict[str, List[str]] = {}


class ChatContextType(Enum):
    """Types of chat contexts"""
    GENERAL = "general"
    PROJECT_CREATION = "project_creation"
    DOCUMENT_UPLOAD = "document_upload"
    REQUIREMENTS_ANALYSIS = "requirements_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"
    BROWNFIELD_ANALYSIS = "brownfield_analysis"
    VIBE_CODING = "vibe_coding"
    WORKFLOW_GUIDANCE = "workflow_guidance"


@dataclass
class ChatMessage:
    """Represents a chat message"""
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    context_type: ChatContextType
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatContext:
    """Represents the context for a chat session"""
    user_id: str
    project_id: Optional[str] = None
    workflow_session_id: Optional[str] = None
    current_page: Optional[str] = None
    context_type: ChatContextType = ChatContextType.GENERAL
    additional_context: Optional[Dict[str, Any]] = None


@dataclass
class ModelInfo:
    """Information about an LLM model"""
    provider: str
    model: str
    display_name: str
    description: str
    capabilities: List[str]
    cost_tier: str  # 'free', 'low', 'medium', 'high'
    speed_tier: str  # 'fast', 'medium', 'slow'
    is_available: bool = True


class AIChatService:
    """AI Chat service for providing contextual assistance"""
    
    def __init__(self):
        self.llm_strategy = LLMStrategy()
        self.available_models = self._initialize_models()
        self.conversation_history: Dict[str, List[ChatMessage]] = {}
    
    def _initialize_models(self) -> Dict[str, ModelInfo]:
        """Initialize available models with their information"""
        return {
            "deepseek-r1": ModelInfo(
                provider="deepseek",
                model="deepseek-r1",
                display_name="DeepSeek R1",
                description="Excellent for general chat, requirements analysis, and code understanding",
                capabilities=["general_chat", "requirements_analysis", "code_analysis", "debugging"],
                cost_tier="free",
                speed_tier="fast",
                is_available=True
            ),
            "claude-opus": ModelInfo(
                provider="anthropic",
                model="claude-3-5-opus-20241022",
                display_name="Claude Opus",
                description="Best for complex reasoning, architecture design, and strategic planning",
                capabilities=["architecture_design", "complex_reasoning", "strategy_planning", "technical_writing"],
                cost_tier="high",
                speed_tier="medium",
                is_available=True
            ),
            "claude-sonnet": ModelInfo(
                provider="anthropic",
                model="claude-3-5-sonnet-20241022",
                display_name="Claude Sonnet",
                description="Great balance of capability and cost for most tasks",
                capabilities=["general_chat", "technical_writing", "code_generation", "analysis"],
                cost_tier="medium",
                speed_tier="fast",
                is_available=True
            ),
            "gpt-4": ModelInfo(
                provider="openai",
                model="gpt-4",
                display_name="GPT-4",
                description="Excellent for code generation and technical problem solving",
                capabilities=["code_generation", "problem_solving", "technical_analysis", "general_chat"],
                cost_tier="high",
                speed_tier="medium",
                is_available=True
            )
        }
    
    async def process_chat_message(
        self,
        message: str,
        context: ChatContext,
        selected_model: Optional[str] = None
    ) -> ChatMessage:
        """
        Process a chat message and generate a response
        
        Args:
            message: User's message
            context: Chat context
            selected_model: User-selected model (optional)
            
        Returns:
            Assistant's response message
            
        Raises:
            AIChatError: If processing fails
            ValidationError: If input is invalid
        """
        try:
            # Validate input
            if not message or not message.strip():
                raise ValidationError("Message cannot be empty")
            
            if not context.user_id:
                raise ValidationError("User ID is required")
            
            # Select optimal model if not specified
            if not selected_model:
                selected_model = self._select_optimal_model(context)
            
            # Validate model selection
            if selected_model not in self.available_models:
                raise ValidationError(f"Invalid model: {selected_model}")
            
            model_info = self.available_models[selected_model]
            if not model_info.is_available:
                raise AIChatError(f"Model {selected_model} is not available")
            
            # Get conversation history
            conversation_id = self._get_conversation_id(context)
            history = self.conversation_history.get(conversation_id, [])
            
            # Create user message
            user_message = ChatMessage(
                id=self._generate_message_id(),
                role="user",
                content=message,
                timestamp=datetime.utcnow(),
                context_type=context.context_type,
                metadata={"selected_model": selected_model}
            )
            
            # Add to history
            history.append(user_message)
            
            # Generate response
            response_content = await self._generate_response(
                message, context, history, selected_model
            )
            
            # Create assistant message
            assistant_message = ChatMessage(
                id=self._generate_message_id(),
                role="assistant",
                content=response_content,
                timestamp=datetime.utcnow(),
                context_type=context.context_type,
                metadata={
                    "model_used": selected_model,
                    "context_type": context.context_type.value
                }
            )
            
            # Add to history
            history.append(assistant_message)
            self.conversation_history[conversation_id] = history
            
            logger.info(
                f"Generated AI response for user {context.user_id}",
                extra={
                    "user_id": context.user_id,
                    "model": selected_model,
                    "context_type": context.context_type.value,
                    "message_length": len(message),
                    "response_length": len(response_content)
                }
            )
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
            raise AIChatError(f"Failed to process chat message: {str(e)}")
    
    def _select_optimal_model(self, context: ChatContext) -> str:
        """Select the optimal model based on context"""
        # Map context types to task types for model selection
        context_to_task = {
            ChatContextType.GENERAL: TaskType.DEVELOPMENT,
            ChatContextType.PROJECT_CREATION: TaskType.REQUIREMENTS_PARSING,
            ChatContextType.DOCUMENT_UPLOAD: TaskType.REQUIREMENTS_PARSING,
            ChatContextType.REQUIREMENTS_ANALYSIS: TaskType.REQUIREMENTS_PARSING,
            ChatContextType.ARCHITECTURE_DESIGN: TaskType.ARCHITECTURE_DESIGN,
            ChatContextType.BROWNFIELD_ANALYSIS: TaskType.GITHUB_ANALYSIS,
            ChatContextType.VIBE_CODING: TaskType.CODE_GENERATION,
            ChatContextType.WORKFLOW_GUIDANCE: TaskType.DEVELOPMENT
        }
        
        task_type = context_to_task.get(context.context_type, TaskType.DEVELOPMENT)
        provider, model = self.llm_strategy.get_llm_for_task(task_type)
        # Map to one of the known keys by provider preference
        if provider == "openai":
            model_key = "gpt-4" if "gpt" in model else "gpt-4"
        elif provider == "anthropic":
            model_key = "claude-sonnet"
        else:
            model_key = "deepseek-r1"
        
        return model_key
    
    async def _generate_response(
        self,
        message: str,
        context: ChatContext,
        history: List[ChatMessage],
        model: str
    ) -> str:
        """Generate AI response using the selected model.
        If OPENAI is configured and selected, call it with chat history; otherwise fall back to rule-based text.
        """
        # Decide provider by selected model or settings
        selected_provider = self.available_models.get(model, ModelInfo("deepseek","","","",[],"free","fast")).provider
        use_openai = (selected_provider == "openai") or (settings.default_llm_provider == "openai")

        # Prefer OpenAI when selected
        if use_openai and settings.openai_api_key:
            try:
                # Build chat messages with a system prompt and truncated history
                system_prompt = self._create_system_prompt(context)
                # Keep last 8 turns for brevity
                recent = history[-16:]
                messages_payload = (
                    [{"role": "system", "content": system_prompt}] +
                    [{"role": m.role, "content": m.content} for m in recent] +
                    [{"role": "user", "content": message}]
                )
                # Lazy import to avoid hard dependency at import time
                try:
                    from openai import AsyncOpenAI  # type: ignore
                except Exception:  # pragma: no cover
                    AsyncOpenAI = None  # type: ignore
                if AsyncOpenAI is None:
                    raise RuntimeError("OpenAI client not available")
                client = AsyncOpenAI(api_key=settings.openai_api_key)
                model_name = settings.default_llm_model or "gpt-4o-mini"
                resp = await client.chat.completions.create(
                    model=model_name,
                    messages=messages_payload,
                    temperature=0.3,
                )
                content = resp.choices[0].message.content if resp.choices else ""
                if not content:
                    content = "I'm here to help. Could you please clarify your request?"
                return content
            except Exception as e:
                logger.error(f"OpenAI generation failed: {e}")
                # Continue to fallback below

        # DeepSeek local (Ollama-compatible) when configured as default
        if selected_provider == "deepseek" or settings.default_llm_provider == "deepseek":
            try:
                system_prompt = self._create_system_prompt(context)
                recent = history[-16:]
                messages_payload = (
                    [{"role": "system", "content": system_prompt}] +
                    [{"role": m.role, "content": m.content} for m in recent] +
                    [{"role": "user", "content": message}]
                )
                model_name = model or settings.deepseek_model or "deepseek-r1:latest"
                base = settings.deepseek_base_url.rstrip("/")
                # Use OpenAI-compatible endpoint
                url = f"{base}/v1/chat/completions"
                async with httpx.AsyncClient(timeout=120) as client:  # Increased timeout
                    resp = await client.post(
                        url,
                        json={
                            "model": model_name,
                            "messages": messages_payload,
                            "stream": False,
                            "temperature": 0.3,
                            "top_p": 0.9,  # Add top_p for better quality
                            "max_tokens": 1000,  # Limit response length for faster generation
                            "options": {
                                "num_ctx": 2048,  # Reduce context window for better performance
                                "num_gpu": 1,  # Limit GPU usage
                            }
                        },
                    )
                resp.raise_for_status()
                data = resp.json()
                # OpenAI-compatible format: {choices: [{message: {content}}]}
                content = (
                    (data.get("choices") or [{}])[0].get("message", {}).get("content")
                    or data.get("message", {}).get("content")
                    or ""
                )
                if not content:
                    content = "I'm here to help. Could you please clarify your request?"
                return content
            except Exception as e:
                logger.error(f"DeepSeek local generation failed: {e}")
                # Try faster model as fallback
                try:
                    faster_model = "deepseek-coder:latest"  # Usually faster than r1
                    logger.info(f"Trying fallback model: {faster_model}")
                    async with httpx.AsyncClient(timeout=60) as client:
                        resp = await client.post(
                            url,
                            json={
                                "model": faster_model,
                                "messages": messages_payload,
                                "stream": False,
                                "temperature": 0.3,
                                "max_tokens": 500,  # Shorter responses for speed
                                "options": {
                                    "num_ctx": 1024,  # Smaller context for speed
                                }
                            },
                        )
                    resp.raise_for_status()
                    data = resp.json()
                    content = (
                        (data.get("choices") or [{}])[0].get("message", {}).get("content")
                        or data.get("message", {}).get("content")
                        or ""
                    )
                    if content:
                        logger.info("Fallback model succeeded")
                        return content
                except Exception as fallback_e:
                    logger.error(f"Fallback model also failed: {fallback_e}")
                # Fall back to template below

        # Fallback: lightweight, context-aware template
        system_prompt = self._create_system_prompt(context)
        if context.context_type == ChatContextType.PROJECT_CREATION:
            return f"{system_prompt} Based on: '{message}'. Let's define scope, stakeholders, and success criteria. What is the main goal?"
        if context.context_type == ChatContextType.ARCHITECTURE_DESIGN:
            return f"{system_prompt} For: '{message}'. Consider requirements → constraints → candidate styles → tradeoffs. What constraints are non‑negotiable?"
        if context.context_type == ChatContextType.VIBE_CODING:
            return f"{system_prompt} For: '{message}'. Share the language/framework and any code so I can assist precisely."
        return f"{system_prompt} You asked: '{message}'. Tell me the most critical detail I should consider first."
    
    def _create_system_prompt(self, context: ChatContext) -> str:
        """Create a context-aware system prompt"""
        base_prompt = "You are ArchMesh AI, an intelligent assistant for architecture design and development workflows."
        
        context_prompts = {
            ChatContextType.PROJECT_CREATION: "You are helping with project creation and setup.",
            ChatContextType.DOCUMENT_UPLOAD: "You are assisting with document upload and analysis.",
            ChatContextType.REQUIREMENTS_ANALYSIS: "You are helping with requirements analysis and clarification.",
            ChatContextType.ARCHITECTURE_DESIGN: "You are providing architecture design guidance and recommendations.",
            ChatContextType.BROWNFIELD_ANALYSIS: "You are assisting with brownfield system analysis and integration.",
            ChatContextType.VIBE_CODING: "You are helping with code generation and programming assistance.",
            ChatContextType.WORKFLOW_GUIDANCE: "You are providing workflow guidance and process assistance."
        }
        
        context_prompt = context_prompts.get(context.context_type, "You are providing general assistance.")
        
        return f"{base_prompt} {context_prompt} Be helpful, accurate, and concise in your responses."
    
    def _get_conversation_id(self, context: ChatContext) -> str:
        """Generate a unique conversation ID based on context"""
        if context.project_id:
            return f"project_{context.project_id}_{context.user_id}"
        elif context.workflow_session_id:
            return f"workflow_{context.workflow_session_id}_{context.user_id}"
        else:
            return f"general_{context.user_id}"
    
    def _generate_message_id(self) -> str:
        """Generate a unique message ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models as serializable dicts"""
        models: List[Dict[str, Any]] = []
        for key, m in self.available_models.items():
            if not m.is_available:
                continue
            models.append({
                "key": key,
                "provider": m.provider,
                "name": m.display_name,
                "description": m.description,
                "capabilities": m.capabilities,
                "cost_tier": m.cost_tier,
                "speed_tier": m.speed_tier,
            })
        return models

    async def get_current_model(self) -> str:
        return "deepseek-r1"

    async def get_default_model(self) -> str:
        return "deepseek-r1"

    async def create_session(self, user_id: str, title: str) -> Dict[str, Any]:
        import uuid
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        session = {
            "id": session_id,
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "messages": [],
            "current_model": "deepseek-r1",
            "context": {},
        }
        _SESSIONS[session_id] = session
        _USER_SESSIONS.setdefault(user_id, []).append(session_id)
        return session

    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for sid in _USER_SESSIONS.get(user_id, []):
            s = _SESSIONS.get(sid)
            if s:
                result.append(s)
        return result

    async def get_session(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        s = _SESSIONS.get(session_id)
        if s and s.get("user_id") == user_id:
            return s
        return None

    async def send_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        session = await self.get_session(session_id, user_id)
        if not session:
            raise ValidationError("Session not found")
        model_key = model or session.get("current_model", "deepseek-r1")
        chat_context = ChatContext(user_id=user_id, context_type=ChatContextType.GENERAL)
        assistant_msg = await self.process_chat_message(content, chat_context, selected_model=model_key)
        # append messages to session
        session["messages"].append({
            "id": self._generate_message_id(),
            "role": "user",
            "content": content,
            "timestamp": datetime.utcnow(),
        })
        session["messages"].append({
            "id": assistant_msg.id,
            "role": assistant_msg.role,
            "content": assistant_msg.content,
            "timestamp": assistant_msg.timestamp,
            "model_used": model_key,
        })
        session["updated_at"] = datetime.utcnow()
        return {
            "success": True,
            "message": {
                "id": assistant_msg.id,
                "content": assistant_msg.content,
                "role": assistant_msg.role,
                "timestamp": assistant_msg.timestamp,
                "model_used": model_key,
                "metadata": assistant_msg.metadata or {},
            },
            "session_id": session_id,
            "model_used": model_key,
        }

    async def switch_model(self, session_id: str, model: str) -> bool:
        if model not in self.available_models:
            return False
        s = _SESSIONS.get(session_id)
        if not s:
            return False
        s["current_model"] = model
        s["updated_at"] = datetime.utcnow()
        return True

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        s = _SESSIONS.get(session_id)
        if not s or s.get("user_id") != user_id:
            return False
        del _SESSIONS[session_id]
        if user_id in _USER_SESSIONS:
            _USER_SESSIONS[user_id] = [sid for sid in _USER_SESSIONS[user_id] if sid != session_id]
        return True
    
    def get_conversation_history(self, context: ChatContext) -> List[ChatMessage]:
        """Get conversation history for a context"""
        conversation_id = self._get_conversation_id(context)
        return self.conversation_history.get(conversation_id, [])
    
    def clear_conversation_history(self, context: ChatContext) -> None:
        """Clear conversation history for a context"""
        conversation_id = self._get_conversation_id(context)
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]
    
    def get_model_recommendations(self, context_type: ChatContextType) -> List[str]:
        """Get model recommendations for a specific context type"""
        recommendations = []
        
        for model_key, model_info in self.available_models.items():
            if not model_info.is_available:
                continue
                
            # Check if model has capabilities for this context
            context_capabilities = {
                ChatContextType.GENERAL: ["general_chat"],
                ChatContextType.PROJECT_CREATION: ["general_chat", "analysis"],
                ChatContextType.DOCUMENT_UPLOAD: ["analysis", "requirements_analysis"],
                ChatContextType.REQUIREMENTS_ANALYSIS: ["requirements_analysis", "analysis"],
                ChatContextType.ARCHITECTURE_DESIGN: ["architecture_design", "complex_reasoning"],
                ChatContextType.BROWNFIELD_ANALYSIS: ["code_analysis", "analysis"],
                ChatContextType.VIBE_CODING: ["code_generation", "debugging"],
                ChatContextType.WORKFLOW_GUIDANCE: ["general_chat", "analysis"]
            }
            
            required_capabilities = context_capabilities.get(context_type, ["general_chat"])
            
            if any(cap in model_info.capabilities for cap in required_capabilities):
                recommendations.append(model_key)
        
        # Sort by cost and speed (prefer free and fast models)
        def sort_key(model_key):
            model = self.available_models[model_key]
            cost_priority = {"free": 0, "low": 1, "medium": 2, "high": 3}
            speed_priority = {"fast": 0, "medium": 1, "slow": 2}
            return (cost_priority.get(model.cost_tier, 3), speed_priority.get(model.speed_tier, 2))
        
        return sorted(recommendations, key=sort_key)

