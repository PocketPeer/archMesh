"""
LLM Usage Examples for ArchMesh PoC.

This module provides practical examples of how to use the optimized LLM strategy
for different tasks in the ArchMesh system.
"""

from typing import Dict, Any
from loguru import logger

from app.core.llm_strategy import LLMStrategy, TaskType, get_optimal_llm_for_task
from app.agents.requirements_agent import RequirementsAgent
from app.agents.architecture_agent import ArchitectureAgent


class LLMUsageExamples:
    """
    Examples demonstrating optimal LLM usage for different tasks.
    """
    
    @staticmethod
    def example_requirements_parsing():
        """
        Example: Requirements parsing with DeepSeek R1 (excellent performance).
        """
        logger.info("=== Requirements Parsing Example ===")
        
        # The RequirementsAgent automatically uses DeepSeek R1 for requirements parsing
        requirements_agent = RequirementsAgent()
        
        # Example usage
        input_data = {
            "document_path": "/path/to/requirements.txt",
            "project_context": "E-commerce platform",
            "domain": "cloud-native",
            "session_id": "req_001"
        }
        
        logger.info(f"Using LLM: {requirements_agent.llm_provider}/{requirements_agent.llm_model}")
        logger.info("This is optimal for requirements parsing according to our analysis")
        
        return requirements_agent
    
    @staticmethod
    def example_architecture_design():
        """
        Example: Architecture design with Claude Opus (best performance).
        """
        logger.info("=== Architecture Design Example ===")
        
        # The ArchitectureAgent automatically uses Claude Opus for architecture design
        architecture_agent = ArchitectureAgent()
        
        # Example usage
        input_data = {
            "requirements": {
                "structured_requirements": {
                    "business_goals": ["Build scalable e-commerce platform"],
                    "functional_requirements": ["User authentication", "Product catalog"],
                    "non_functional_requirements": {
                        "performance": ["Handle 10k concurrent users"],
                        "security": ["PCI DSS compliance"]
                    }
                }
            },
            "domain": "cloud-native",
            "session_id": "arch_001"
        }
        
        logger.info(f"Using LLM: {architecture_agent.llm_provider}/{architecture_agent.llm_model}")
        logger.info("This is optimal for architecture design according to our analysis")
        
        return architecture_agent
    
    @staticmethod
    def example_manual_llm_selection():
        """
        Example: Manual LLM selection for specific tasks.
        """
        logger.info("=== Manual LLM Selection Example ===")
        
        # Get optimal LLM for different tasks
        tasks = [
            TaskType.REQUIREMENTS_PARSING,
            TaskType.ARCHITECTURE_DESIGN,
            TaskType.CODE_GENERATION,
            TaskType.GITHUB_ANALYSIS,
            TaskType.ADR_WRITING,
            TaskType.DEVELOPMENT,
            TaskType.TESTING
        ]
        
        for task in tasks:
            provider, model = LLMStrategy.get_llm_for_task(task)
            logger.info(f"{task.value}: {provider}/{model}")
        
        return tasks
    
    @staticmethod
    def example_environment_specific_selection():
        """
        Example: Environment-specific LLM selection.
        """
        logger.info("=== Environment-Specific Selection Example ===")
        
        # Development environment (cost-optimized)
        dev_provider, dev_model = LLMStrategy.get_llm_for_task(
            TaskType.CODE_GENERATION, 
            environment="development"
        )
        logger.info(f"Development - Code Generation: {dev_provider}/{dev_model}")
        
        # Production environment (performance-optimized)
        prod_provider, prod_model = LLMStrategy.get_llm_for_task(
            TaskType.CODE_GENERATION, 
            environment="production"
        )
        logger.info(f"Production - Code Generation: {prod_provider}/{prod_model}")
        
        return {
            "development": (dev_provider, dev_model),
            "production": (prod_provider, prod_model)
        }
    
    @staticmethod
    def example_fallback_handling():
        """
        Example: Handling LLM provider fallbacks.
        """
        logger.info("=== Fallback Handling Example ===")
        
        # Try to get the best LLM, with fallback if unavailable
        try:
            provider, model = LLMStrategy.get_llm_for_task(
                TaskType.ARCHITECTURE_DESIGN,
                use_fallback=True
            )
            logger.info(f"Architecture Design (with fallback): {provider}/{model}")
        except Exception as e:
            logger.error(f"Error getting LLM: {str(e)}")
            # Use default fallback
            provider, model = "deepseek", "deepseek-r1"
            logger.info(f"Using default fallback: {provider}/{model}")
        
        return provider, model
    
    @staticmethod
    def example_get_recommendations():
        """
        Example: Getting comprehensive LLM recommendations.
        """
        logger.info("=== LLM Recommendations Example ===")
        
        # Get all task recommendations
        recommendations = LLMStrategy.get_task_recommendations()
        
        for task, config in recommendations.items():
            logger.info(f"{task}:")
            logger.info(f"  Primary: {config['primary']}")
            logger.info(f"  Alternatives: {config['alternatives']}")
        
        return recommendations
    
    @staticmethod
    def example_environment_strategy():
        """
        Example: Getting environment-specific strategy.
        """
        logger.info("=== Environment Strategy Example ===")
        
        # Get strategy for different environments
        environments = ["development", "production", "staging"]
        
        for env in environments:
            strategy = LLMStrategy.get_environment_strategy(env)
            logger.info(f"{env.upper()} Strategy:")
            logger.info(f"  Approach: {strategy['strategy']}")
            logger.info(f"  Reasoning: {strategy['reasoning']}")
            logger.info(f"  Primary Provider: {strategy['primary_provider']}")
            logger.info(f"  Notes: {strategy['notes']}")
        
        return environments


def demonstrate_llm_optimization():
    """
    Demonstrate the complete LLM optimization strategy.
    """
    logger.info("=== ArchMesh LLM Optimization Demonstration ===")
    
    examples = LLMUsageExamples()
    
    # Run all examples
    examples.example_requirements_parsing()
    examples.example_architecture_design()
    examples.example_manual_llm_selection()
    examples.example_environment_specific_selection()
    examples.example_fallback_handling()
    examples.example_get_recommendations()
    examples.example_environment_strategy()
    
    logger.info("=== Demonstration Complete ===")


if __name__ == "__main__":
    demonstrate_llm_optimization()
