"""
Requirements Extractor - LLM-powered component for extracting requirements
"""

import re
from typing import List, Dict, Any
from .models import ParsedInput, ExtractedRequirements, ExtractedRequirement, RequirementType
from ..llm_service import SimpleLLMService


class RequirementsExtractor:
    """
    Requirements extractor using real LLM calls for accurate extraction.
    
    Single responsibility: Extract requirements from parsed input using AI
    """
    
    def __init__(self):
        self.llm_service = SimpleLLMService()
        
        # Fallback patterns for when LLM is unavailable
        self.business_goal_patterns = [
            r'increase\s+(sales|revenue|profit)',
            r'improve\s+(efficiency|productivity|performance)',
            r'reduce\s+(costs|time|effort)',
            r'enhance\s+(user\s+experience|customer\s+satisfaction)',
            r'expand\s+(market|business|reach)',
            r'need\s+(a|an|the)\s+\w+\s+(system|application|platform)',
            r'want\s+to\s+\w+',
            r'goal\s+is\s+to\s+\w+'
        ]
        
        self.functional_patterns = [
            r'user\s+(can|should|must|will)\s+(\w+)',
            r'system\s+(should|must|will)\s+(\w+)',
            r'(\w+)\s+(feature|function|capability)',
            r'(\w+)\s+(management|handling|processing)',
            r'able\s+to\s+(\w+)',
            r'should\s+be\s+able\s+to\s+(\w+)',
            r'create\s+(\w+)',
            r'manage\s+(\w+)'
        ]
        
        self.non_functional_patterns = [
            r'(performance|speed|response\s+time)',
            r'(security|privacy|protection)',
            r'(scalability|availability|reliability)',
            r'(usability|accessibility|compatibility)',
            r'(secure|fast|reliable)',
            r'(handle\s+\d+|\d+\s+concurrent)',
            r'(high\s+performance|low\s+latency)'
        ]
        
        self.constraint_patterns = [
            r'(budget|cost|price)',
            r'(time|deadline|schedule)',
            r'(technology|platform|framework)',
            r'(compliance|regulation|standard)',
            r'\$\d+',
            r'\d+\s+months?',
            r'\d+\s+weeks?',
            r'\d+\s+days?'
        ]
        
        self.stakeholder_patterns = [
            r'(user|customer|client)',
            r'(admin|administrator|manager)',
            r'(developer|engineer|programmer)',
            r'(stakeholder|owner|sponsor)',
            r'(customers|administrators)'
        ]
    
    async def extract(self, parsed_input: ParsedInput) -> ExtractedRequirements:
        """
        Extract requirements from parsed input using LLM.
        
        Args:
            parsed_input: Parsed user input
            
        Returns:
            ExtractedRequirements: Structured requirements
        """
        try:
            # Use LLM to extract requirements
            llm_result = await self.llm_service.extract_requirements(parsed_input.text)
            
            # Convert LLM result to our data structure
            business_goals = self._convert_requirements(llm_result.get("business_goals", []), RequirementType.BUSINESS_GOAL)
            functional_requirements = self._convert_requirements(llm_result.get("functional_requirements", []), RequirementType.FUNCTIONAL)
            non_functional_requirements = self._convert_requirements(llm_result.get("non_functional_requirements", []), RequirementType.NON_FUNCTIONAL)
            constraints = self._convert_requirements(llm_result.get("constraints", []), RequirementType.CONSTRAINT)
            stakeholders = self._convert_requirements(llm_result.get("stakeholders", []), RequirementType.STAKEHOLDER)
            
            return ExtractedRequirements(
                business_goals=business_goals,
                functional_requirements=functional_requirements,
                non_functional_requirements=non_functional_requirements,
                constraints=constraints,
                stakeholders=stakeholders
            )
            
        except Exception as e:
            # Fallback to pattern matching if LLM fails
            return self._fallback_extraction(parsed_input)
    
    def _convert_requirements(self, llm_requirements: List[Dict], req_type: RequirementType) -> List[ExtractedRequirement]:
        """Convert LLM response to ExtractedRequirement objects."""
        requirements = []
        
        for i, req in enumerate(llm_requirements):
            requirements.append(ExtractedRequirement(
                id=req.get("id", f"{req_type.value}_{i}"),
                type=req_type,
                title=req.get("title", f"{req_type.value.replace('_', ' ').title()} {i+1}"),
                description=req.get("description", ""),
                priority=req.get("priority", "medium"),
                confidence=req.get("confidence", 0.8)
            ))
        
        return requirements
    
    def _fallback_extraction(self, parsed_input: ParsedInput) -> ExtractedRequirements:
        """Fallback to pattern matching if LLM fails."""
        text = parsed_input.text.lower()
        
        business_goals = self._extract_by_type(text, RequirementType.BUSINESS_GOAL, self.business_goal_patterns)
        functional = self._extract_by_type(text, RequirementType.FUNCTIONAL, self.functional_patterns)
        non_functional = self._extract_by_type(text, RequirementType.NON_FUNCTIONAL, self.non_functional_patterns)
        constraints = self._extract_by_type(text, RequirementType.CONSTRAINT, self.constraint_patterns)
        stakeholders = self._extract_by_type(text, RequirementType.STAKEHOLDER, self.stakeholder_patterns)
        
        return ExtractedRequirements(
            business_goals=business_goals,
            functional_requirements=functional,
            non_functional_requirements=non_functional,
            constraints=constraints,
            stakeholders=stakeholders
        )
    
    def _extract_by_type(self, text: str, req_type: RequirementType, patterns: List[str]) -> List[ExtractedRequirement]:
        """Extract requirements of a specific type using patterns."""
        requirements = []
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for j, match in enumerate(matches):
                requirement = ExtractedRequirement(
                    id=f"{req_type.value}_{i}_{j}",
                    type=req_type,
                    title=self._generate_title(match.group(), req_type),
                    description=self._generate_description(match.group(), req_type),
                    priority=self._determine_priority(match.group(), req_type),
                    confidence=self._calculate_confidence(match.group(), req_type)
                )
                requirements.append(requirement)
        
        return requirements
    
    def _generate_title(self, match: str, req_type: RequirementType) -> str:
        """Generate a simple title for the requirement"""
        if req_type == RequirementType.BUSINESS_GOAL:
            return f"Business Goal: {match.title()}"
        elif req_type == RequirementType.FUNCTIONAL:
            return f"Functional Requirement: {match.title()}"
        elif req_type == RequirementType.NON_FUNCTIONAL:
            return f"Non-Functional Requirement: {match.title()}"
        elif req_type == RequirementType.CONSTRAINT:
            return f"Constraint: {match.title()}"
        elif req_type == RequirementType.STAKEHOLDER:
            return f"Stakeholder: {match.title()}"
        else:
            return f"Requirement: {match.title()}"
    
    def _generate_description(self, match: str, req_type: RequirementType) -> str:
        """Generate a simple description for the requirement"""
        base_desc = f"This requirement relates to {match.lower()}"
        
        if req_type == RequirementType.BUSINESS_GOAL:
            return f"{base_desc} and supports business objectives."
        elif req_type == RequirementType.FUNCTIONAL:
            return f"{base_desc} and defines system functionality."
        elif req_type == RequirementType.NON_FUNCTIONAL:
            return f"{base_desc} and defines system quality attributes."
        elif req_type == RequirementType.CONSTRAINT:
            return f"{base_desc} and limits system design options."
        elif req_type == RequirementType.STAKEHOLDER:
            return f"{base_desc} and identifies system users."
        else:
            return f"{base_desc}."
    
    def _determine_priority(self, match: str, req_type: RequirementType) -> str:
        """Simple priority determination"""
        high_priority_words = ['must', 'critical', 'essential', 'required']
        medium_priority_words = ['should', 'important', 'recommended']
        
        match_lower = match.lower()
        
        if any(word in match_lower for word in high_priority_words):
            return "high"
        elif any(word in match_lower for word in medium_priority_words):
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, match: str, req_type: RequirementType) -> float:
        """Simple confidence calculation"""
        confidence = 0.5  # Base confidence
        
        # Length factor
        if len(match) > 20:
            confidence += 0.2
        
        # Specificity factor
        if any(word in match.lower() for word in ['specific', 'detailed', 'precise']):
            confidence += 0.2
        
        # Clarity factor
        if match.count(' ') > 2:  # More than 2 words
            confidence += 0.1
        
        return min(confidence, 1.0)