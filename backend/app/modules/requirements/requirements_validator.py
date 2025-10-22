"""
Requirements Validator - Simple component for validating requirements
"""

from typing import List
from .models import ExtractedRequirements, ValidationResult, ValidationStatus


class RequirementsValidator:
    """
    Simple requirements validator that checks quality and completeness.
    
    Single responsibility: Validate extracted requirements
    """
    
    def __init__(self):
        self.min_requirements_per_type = 1
        self.min_description_length = 10
        self.min_confidence_threshold = 0.3
    
    def validate(self, requirements: ExtractedRequirements) -> ValidationResult:
        """
        Validate extracted requirements for quality and completeness.
        
        Args:
            requirements: Extracted requirements to validate
            
        Returns:
            ValidationResult: Validation status and feedback
        """
        issues = []
        suggestions = []
        score = 0.0
        
        # Check completeness
        completeness_score = self._check_completeness(requirements)
        score += completeness_score * 0.4
        
        if completeness_score < 0.5:
            issues.append("Requirements are incomplete")
            suggestions.append("Add more business goals, functional requirements, and constraints")
        
        # Check quality
        quality_score = self._check_quality(requirements)
        score += quality_score * 0.3
        
        if quality_score < 0.5:
            issues.append("Requirements quality is low")
            suggestions.append("Improve requirement descriptions and clarity")
        
        # Check confidence
        confidence_score = self._check_confidence(requirements)
        score += confidence_score * 0.3
        
        if confidence_score < 0.5:
            issues.append("Low confidence in requirement extraction")
            suggestions.append("Provide more detailed and specific requirements")
        
        # Determine overall status
        if score >= 0.8:
            status = ValidationStatus.VALID
        elif score >= 0.5:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.INVALID
        
        return ValidationResult(
            status=status,
            score=score,
            issues=issues,
            suggestions=suggestions
        )
    
    def _check_completeness(self, requirements: ExtractedRequirements) -> float:
        """Check if requirements are complete"""
        score = 0.0
        
        # Check if we have at least one of each type
        if requirements.business_goals:
            score += 0.2
        if requirements.functional_requirements:
            score += 0.2
        if requirements.non_functional_requirements:
            score += 0.2
        if requirements.constraints:
            score += 0.2
        if requirements.stakeholders:
            score += 0.2
        
        return score
    
    def _check_quality(self, requirements: ExtractedRequirements) -> float:
        """Check quality of requirements"""
        all_requirements = (
            requirements.business_goals +
            requirements.functional_requirements +
            requirements.non_functional_requirements +
            requirements.constraints +
            requirements.stakeholders
        )
        
        if not all_requirements:
            return 0.0
        
        quality_scores = []
        
        for req in all_requirements:
            req_score = 0.0
            
            # Description length
            if len(req.description) >= self.min_description_length:
                req_score += 0.3
            
            # Title quality
            if len(req.title) > 10:
                req_score += 0.2
            
            # Priority assignment
            if req.priority in ['high', 'medium', 'low']:
                req_score += 0.2
            
            # Confidence level
            if req.confidence >= self.min_confidence_threshold:
                req_score += 0.3
            
            quality_scores.append(req_score)
        
        return sum(quality_scores) / len(quality_scores)
    
    def _check_confidence(self, requirements: ExtractedRequirements) -> float:
        """Check confidence levels of requirements"""
        all_requirements = (
            requirements.business_goals +
            requirements.functional_requirements +
            requirements.non_functional_requirements +
            requirements.constraints +
            requirements.stakeholders
        )
        
        if not all_requirements:
            return 0.0
        
        confidence_scores = [req.confidence for req in all_requirements]
        return sum(confidence_scores) / len(confidence_scores)
