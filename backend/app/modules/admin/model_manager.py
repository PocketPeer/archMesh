"""
Model Manager - Handles LLM model configurations and selection
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from .models import ModelConfig, ModelProvider, ModelStatus


class ModelManager:
    """
    Manages LLM model configurations and selection.
    
    Responsibilities:
    - Model configuration management
    - Model selection based on task type
    - Cost optimization
    - Performance monitoring
    """
    
    def __init__(self):
        self.models: List[ModelConfig] = []
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize default model configurations"""
        default_models = [
            ModelConfig(
                id="gpt-4o-mini",
                name="GPT-4o Mini",
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o-mini",
                cost_per_1k_tokens={"prompt": 0.00015, "completion": 0.0006},
                max_tokens=4000,
                temperature=0.3,
                timeout_seconds=120,
                is_default=True
            ),
            ModelConfig(
                id="gpt-4o",
                name="GPT-4o",
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o",
                cost_per_1k_tokens={"prompt": 0.005, "completion": 0.015},
                max_tokens=4000,
                temperature=0.3,
                timeout_seconds=30
            ),
            ModelConfig(
                id="claude-3-sonnet",
                name="Claude 3 Sonnet",
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-sonnet-20240229",
                cost_per_1k_tokens={"prompt": 0.003, "completion": 0.015},
                max_tokens=4000,
                temperature=0.3,
                timeout_seconds=30
            ),
            ModelConfig(
                id="deepseek-r1",
                name="DeepSeek R1",
                provider=ModelProvider.DEEPSEEK,
                model_name="deepseek-r1",
                cost_per_1k_tokens={"prompt": 0.0, "completion": 0.0},  # Free local model
                max_tokens=4000,
                temperature=0.3,
                timeout_seconds=300  # Increased to 5 minutes for complex reasoning
            ),
            ModelConfig(
                id="llama3.2-3b",
                name="Llama 3.2 3B",
                provider=ModelProvider.OLLAMA,
                model_name="llama3.2:3b",
                cost_per_1k_tokens={"prompt": 0.0, "completion": 0.0},  # Free local model
                max_tokens=4000,
                temperature=0.3,
                timeout_seconds=120
            )
        ]
        
        self.models = default_models
        logger.info(f"Initialized {len(self.models)} model configurations")
    
    def get_available_models(self) -> List[ModelConfig]:
        """Get all available models"""
        return [model for model in self.models if model.status == ModelStatus.ACTIVE]
    
    def get_model_by_id(self, model_id: str) -> Optional[ModelConfig]:
        """Get a specific model by ID"""
        for model in self.models:
            if model.id == model_id:
                return model
        return None
    
    def update_model_timeout(self, model_id: str, timeout_seconds: int) -> bool:
        """Update model timeout"""
        for model in self.models:
            if model.id == model_id:
                model.timeout_seconds = timeout_seconds
                model.updated_at = datetime.now()
                logger.info(f"Updated timeout for model {model_id} to {timeout_seconds} seconds")
                return True
        logger.warning(f"Model {model_id} not found for timeout update")
        return False
    
    def get_default_model(self) -> Optional[ModelConfig]:
        """Get the default model configuration"""
        for model in self.models:
            if model.is_default and model.status == ModelStatus.ACTIVE:
                return model
        return None
    
    def get_models_by_provider(self, provider: ModelProvider) -> List[ModelConfig]:
        """Get models by provider"""
        return [model for model in self.models 
                if model.provider == provider and model.status == ModelStatus.ACTIVE]
    
    def select_optimal_model(self, task_type: str, budget_limit: Optional[float] = None) -> Optional[ModelConfig]:
        """
        Select the optimal model for a given task type and budget.
        
        Args:
            task_type: Type of task (requirements, architecture, code_generation, etc.)
            budget_limit: Maximum cost per request
            
        Returns:
            Optimal model configuration
        """
        available_models = self.get_available_models()
        
        if not available_models:
            logger.warning("No available models found")
            return None
        
        # Task-specific model preferences
        task_preferences = {
            "requirements": ["gpt-4o-mini", "claude-3-sonnet", "deepseek-r1"],
            "architecture": ["gpt-4o", "claude-3-sonnet", "deepseek-r1"],
            "code_generation": ["gpt-4o", "claude-3-sonnet", "llama3.2-3b"],
            "analysis": ["gpt-4o", "claude-3-sonnet", "deepseek-r1"],
            "default": ["gpt-4o-mini", "deepseek-r1", "llama3.2-3b"]
        }
        
        preferred_models = task_preferences.get(task_type, task_preferences["default"])
        
        # Filter by budget if specified
        if budget_limit is not None:
            available_models = [
                model for model in available_models
                if model.cost_per_1k_tokens.get("prompt", 0) <= budget_limit
            ]
        
        # Select first available preferred model
        for preferred_id in preferred_models:
            for model in available_models:
                if model.id == preferred_id:
                    logger.info(f"Selected model {model.name} for task {task_type}")
                    return model
        
        # Fallback to first available model
        logger.info(f"Using fallback model {available_models[0].name} for task {task_type}")
        return available_models[0]
    
    def calculate_cost(self, model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for a model usage"""
        model = self.get_model_by_id(model_id)
        if not model:
            return 0.0
        
        prompt_cost = (prompt_tokens / 1000) * model.cost_per_1k_tokens.get("prompt", 0)
        completion_cost = (completion_tokens / 1000) * model.cost_per_1k_tokens.get("completion", 0)
        
        return prompt_cost + completion_cost
    
    def update_model_status(self, model_id: str, status: ModelStatus) -> bool:
        """Update model status"""
        model = self.get_model_by_id(model_id)
        if not model:
            return False
        
        model.status = status
        model.updated_at = datetime.now()
        logger.info(f"Updated model {model.name} status to {status}")
        return True
    
    def add_custom_model(self, model_config: ModelConfig) -> bool:
        """Add a custom model configuration"""
        # Check if model ID already exists
        if self.get_model_by_id(model_config.id):
            logger.warning(f"Model {model_config.id} already exists")
            return False
        
        self.models.append(model_config)
        logger.info(f"Added custom model {model_config.name}")
        return True
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """Get model usage statistics"""
        stats = {
            "total_models": len(self.models),
            "active_models": len(self.get_available_models()),
            "models_by_provider": {},
            "cost_analysis": {}
        }
        
        # Count by provider
        for provider in ModelProvider:
            count = len(self.get_models_by_provider(provider))
            stats["models_by_provider"][provider.value] = count
        
        # Cost analysis
        free_models = [m for m in self.models if m.cost_per_1k_tokens.get("prompt", 0) == 0]
        paid_models = [m for m in self.models if m.cost_per_1k_tokens.get("prompt", 0) > 0]
        
        stats["cost_analysis"] = {
            "free_models": len(free_models),
            "paid_models": len(paid_models),
            "cheapest_model": min(self.models, key=lambda m: m.cost_per_1k_tokens.get("prompt", float('inf'))).name if self.models else None
        }
        
        return stats
