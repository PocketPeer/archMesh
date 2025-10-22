"""
Workflow Refinement Service

This module implements the multi-LLM workflow refinement system that allows
iterative improvement of workflow outputs using different LLMs for validation,
critique, and enhancement.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from app.core.llm_strategy import LLMStrategy
from app.models.workflow_session import WorkflowSession
from app.core.database import get_db

logger = logging.getLogger(__name__)


class RefinementStrategy(Enum):
    """Refinement strategy types"""
    VALIDATION_ONLY = "validation_only"
    CROSS_VALIDATION = "cross_validation"
    ITERATIVE_IMPROVEMENT = "iterative_improvement"
    MULTI_LLM_SYNTHESIS = "multi_llm_synthesis"


class QualityLevel(Enum):
    """Quality assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXCELLENT = "excellent"


@dataclass
class RefinementConfig:
    """Configuration for workflow refinement"""
    strategy: RefinementStrategy
    primary_llm: str
    validation_llm: str
    refinement_llm: str
    max_iterations: int = 3
    quality_threshold: float = 0.8
    enable_cross_validation: bool = True
    enable_question_generation: bool = True


@dataclass
class QualityScore:
    """Quality assessment result"""
    completeness: float
    consistency: float
    accuracy: float
    relevance: float
    overall: float
    confidence: float


@dataclass
class RefinementResult:
    """Result of workflow refinement"""
    original_output: Dict[str, Any]
    refined_output: Dict[str, Any]
    quality_improvement: float
    iterations_performed: int
    llm_used: str
    refinement_notes: List[str]
    questions_generated: List[Dict[str, Any]]
    timestamp: datetime


class WorkflowRefinementService:
    """Service for refining workflow outputs using multiple LLMs"""
    
    def __init__(self):
        self.llm_strategy = LLMStrategy()
        self.quality_criteria = {
            "completeness": "How complete and comprehensive is the output?",
            "consistency": "How consistent is the output with requirements?",
            "accuracy": "How accurate are the technical details?",
            "relevance": "How relevant is the output to the project goals?"
        }
    
    async def refine_workflow_output(
        self,
        workflow_id: str,
        config: RefinementConfig,
        user_context: Optional[Dict[str, Any]] = None
    ) -> RefinementResult:
        """
        Refine a workflow output using multi-LLM orchestration
        
        Args:
            workflow_id: ID of the workflow to refine
            config: Refinement configuration
            user_context: Additional user context for refinement
            
        Returns:
            RefinementResult with improved output and metadata
        """
        try:
            # Get original workflow output
            original_output = await self._get_workflow_output(workflow_id)
            if not original_output:
                raise ValueError(f"Workflow {workflow_id} not found or has no output")
            
            # Initialize refinement process
            refinement_notes = []
            questions_generated = []
            iterations = 0
            current_output = original_output.copy()
            
            # Perform iterative refinement
            while iterations < config.max_iterations:
                logger.info(f"Refinement iteration {iterations + 1} for workflow {workflow_id}")
                
                # Validate current output
                validation_result = await self._validate_output(
                    current_output, config.validation_llm, workflow_id
                )
                
                # Check if quality threshold is met
                if validation_result.overall >= config.quality_threshold:
                    logger.info(f"Quality threshold met: {validation_result.overall}")
                    break
                
                # Generate questions if needed
                if config.enable_question_generation and validation_result.overall < 0.7:
                    questions = await self._generate_questions(
                        current_output, workflow_id, user_context
                    )
                    questions_generated.extend(questions)
                
                # Refine output
                refined_output = await self._refine_output(
                    current_output, config.refinement_llm, validation_result, workflow_id
                )
                
                # Cross-validate if enabled
                if config.enable_cross_validation:
                    cross_validation = await self._cross_validate(
                        current_output, refined_output, config.validation_llm
                    )
                    if cross_validation["improvement"] < 0.1:  # Minimal improvement
                        logger.info("Cross-validation shows minimal improvement, stopping")
                        break
                
                current_output = refined_output
                iterations += 1
                
                refinement_notes.append(f"Iteration {iterations}: Quality improved to {validation_result.overall}")
            
            # Calculate quality improvement
            final_validation = await self._validate_output(
                current_output, config.validation_llm, workflow_id
            )
            quality_improvement = final_validation.overall - validation_result.overall
            
            return RefinementResult(
                original_output=original_output,
                refined_output=current_output,
                quality_improvement=quality_improvement,
                iterations_performed=iterations,
                llm_used=config.refinement_llm,
                refinement_notes=refinement_notes,
                questions_generated=questions_generated,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error refining workflow {workflow_id}: {str(e)}")
            raise
    
    async def _get_workflow_output(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the current output of a workflow"""
        try:
            # This would integrate with your existing workflow system
            # For now, return a mock structure
            return {
                "requirements": {},
                "architecture": {},
                "status": "completed"
            }
        except Exception as e:
            logger.error(f"Error getting workflow output: {str(e)}")
            return None
    
    async def _validate_output(
        self, 
        output: Dict[str, Any], 
        llm_provider: str, 
        workflow_id: str
    ) -> QualityScore:
        """Validate output quality using specified LLM"""
        try:
            validation_prompt = self._create_validation_prompt(output, workflow_id)
            
            # Use LLM strategy to get validation
            response = await self.llm_strategy.get_llm_response(
                prompt=validation_prompt,
                provider=llm_provider,
                task_type="validation"
            )
            
            # Parse quality scores from response
            quality_data = self._parse_quality_response(response)
            
            return QualityScore(
                completeness=quality_data.get("completeness", 0.5),
                consistency=quality_data.get("consistency", 0.5),
                accuracy=quality_data.get("accuracy", 0.5),
                relevance=quality_data.get("relevance", 0.5),
                overall=quality_data.get("overall", 0.5),
                confidence=quality_data.get("confidence", 0.5)
            )
            
        except Exception as e:
            logger.error(f"Error validating output: {str(e)}")
            # Return default quality scores
            return QualityScore(0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
    
    async def _generate_questions(
        self, 
        output: Dict[str, Any], 
        workflow_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate questions to improve output quality"""
        try:
            question_prompt = self._create_question_generation_prompt(output, user_context)
            
            response = await self.llm_strategy.get_llm_response(
                prompt=question_prompt,
                provider="claude",  # Use Claude for question generation
                task_type="question_generation"
            )
            
            return self._parse_questions_response(response)
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return []
    
    async def _refine_output(
        self,
        current_output: Dict[str, Any],
        llm_provider: str,
        validation_result: QualityScore,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Refine output using specified LLM"""
        try:
            refinement_prompt = self._create_refinement_prompt(
                current_output, validation_result, workflow_id
            )
            
            response = await self.llm_strategy.get_llm_response(
                prompt=refinement_prompt,
                provider=llm_provider,
                task_type="refinement"
            )
            
            return self._parse_refinement_response(response)
            
        except Exception as e:
            logger.error(f"Error refining output: {str(e)}")
            return current_output
    
    async def _cross_validate(
        self,
        original: Dict[str, Any],
        refined: Dict[str, Any],
        llm_provider: str
    ) -> Dict[str, Any]:
        """Cross-validate refinement improvement"""
        try:
            cross_validation_prompt = self._create_cross_validation_prompt(original, refined)
            
            response = await self.llm_strategy.get_llm_response(
                prompt=cross_validation_prompt,
                provider=llm_provider,
                task_type="cross_validation"
            )
            
            return self._parse_cross_validation_response(response)
            
        except Exception as e:
            logger.error(f"Error in cross-validation: {str(e)}")
            return {"improvement": 0.0, "notes": "Cross-validation failed"}
    
    def _create_validation_prompt(self, output: Dict[str, Any], workflow_id: str) -> str:
        """Create validation prompt for quality assessment"""
        return f"""
        Please evaluate the quality of this workflow output for workflow {workflow_id}:
        
        Output: {json.dumps(output, indent=2)}
        
        Please assess the following criteria on a scale of 0.0 to 1.0:
        1. Completeness: How complete and comprehensive is the output?
        2. Consistency: How consistent is the output with requirements?
        3. Accuracy: How accurate are the technical details?
        4. Relevance: How relevant is the output to the project goals?
        
        Provide your assessment in JSON format:
        {{
            "completeness": 0.0-1.0,
            "consistency": 0.0-1.0,
            "accuracy": 0.0-1.0,
            "relevance": 0.0-1.0,
            "overall": 0.0-1.0,
            "confidence": 0.0-1.0,
            "notes": "Brief explanation of assessment"
        }}
        """
    
    def _create_question_generation_prompt(
        self, 
        output: Dict[str, Any], 
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create prompt for generating improvement questions"""
        context_str = f"User Context: {json.dumps(user_context, indent=2)}" if user_context else ""
        
        return f"""
        Based on this workflow output, generate specific questions that would help improve its quality:
        
        Output: {json.dumps(output, indent=2)}
        {context_str}
        
        Generate 3-5 targeted questions that would help clarify or improve:
        1. Missing information
        2. Unclear requirements
        3. Technical specifications
        4. Business context
        5. Implementation details
        
        Provide questions in JSON format:
        [
            {{
                "question": "What is the expected user load?",
                "category": "technical",
                "priority": "high",
                "context": "Needed for scalability decisions"
            }}
        ]
        """
    
    def _create_refinement_prompt(
        self,
        current_output: Dict[str, Any],
        validation_result: QualityScore,
        workflow_id: str
    ) -> str:
        """Create refinement prompt for improving output"""
        return f"""
        Please improve this workflow output based on the quality assessment:
        
        Current Output: {json.dumps(current_output, indent=2)}
        
        Quality Assessment:
        - Completeness: {validation_result.completeness}
        - Consistency: {validation_result.consistency}
        - Accuracy: {validation_result.accuracy}
        - Relevance: {validation_result.relevance}
        - Overall: {validation_result.overall}
        
        Focus on improving the areas with low scores. Provide an enhanced version of the output
        that addresses the identified weaknesses while maintaining the original structure.
        
        Return the improved output in the same JSON format as the original.
        """
    
    def _create_cross_validation_prompt(
        self,
        original: Dict[str, Any],
        refined: Dict[str, Any]
    ) -> str:
        """Create cross-validation prompt"""
        return f"""
        Compare these two workflow outputs and assess the improvement:
        
        Original: {json.dumps(original, indent=2)}
        Refined: {json.dumps(refined, indent=2)}
        
        Provide assessment in JSON format:
        {{
            "improvement": 0.0-1.0,
            "notes": "Description of improvements made",
            "areas_improved": ["list", "of", "improved", "areas"]
        }}
        """
    
    def _parse_quality_response(self, response: str) -> Dict[str, float]:
        """Parse quality assessment response"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                quality_data = json.loads(response[json_start:json_end])
                return quality_data
        except Exception as e:
            logger.error(f"Error parsing quality response: {str(e)}")
        
        # Return default values if parsing fails
        return {
            "completeness": 0.5,
            "consistency": 0.5,
            "accuracy": 0.5,
            "relevance": 0.5,
            "overall": 0.5,
            "confidence": 0.5
        }
    
    def _parse_questions_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse questions generation response"""
        try:
            # Extract JSON array from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                questions = json.loads(response[json_start:json_end])
                return questions
        except Exception as e:
            logger.error(f"Error parsing questions response: {str(e)}")
        
        return []
    
    def _parse_refinement_response(self, response: str) -> Dict[str, Any]:
        """Parse refinement response"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                refined_output = json.loads(response[json_start:json_end])
                return refined_output
        except Exception as e:
            logger.error(f"Error parsing refinement response: {str(e)}")
        
        # Return original if parsing fails
        return {}
    
    def _parse_cross_validation_response(self, response: str) -> Dict[str, Any]:
        """Parse cross-validation response"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                validation = json.loads(response[json_start:json_end])
                return validation
        except Exception as e:
            logger.error(f"Error parsing cross-validation response: {str(e)}")
        
        return {"improvement": 0.0, "notes": "Cross-validation parsing failed"}


# Factory function for creating refinement service
def get_refinement_service() -> WorkflowRefinementService:
    """Get workflow refinement service instance"""
    return WorkflowRefinementService()
