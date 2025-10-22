"""
Input Parser - Simple component for parsing user input
"""

import re
from typing import Optional, Dict, Any
from .models import ParsedInput, InputType


class InputParser:
    """
    Simple input parser that converts user input into structured data.
    
    Single responsibility: Parse user input into ParsedInput structure
    """
    
    def __init__(self):
        self.max_length = 10000  # Simple limit
        self.min_length = 10    # Simple minimum
    
    def parse(self, input_text: str, input_type: InputType = InputType.TEXT) -> ParsedInput:
        """
        Parse user input into structured format.
        
        Args:
            input_text: Raw user input
            input_type: Type of input (text, file, url)
            
        Returns:
            ParsedInput: Structured input data
        """
        # Simple validation
        if not input_text or len(input_text.strip()) < self.min_length:
            raise ValueError(f"Input too short. Minimum {self.min_length} characters required.")
        
        if len(input_text) > self.max_length:
            raise ValueError(f"Input too long. Maximum {self.max_length} characters allowed.")
        
        # Simple text processing
        cleaned_text = self._clean_text(input_text)
        confidence = self._calculate_confidence(cleaned_text)
        metadata = self._extract_metadata(cleaned_text)
        
        return ParsedInput(
            text=cleaned_text,
            input_type=input_type,
            metadata=metadata,
            confidence=confidence
        )
    
    def _clean_text(self, text: str) -> str:
        """Simple text cleaning"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        cleaned = re.sub(r'[^\w\s.,!?\-]', '', cleaned)
        
        return cleaned
    
    def _calculate_confidence(self, text: str) -> float:
        """Simple confidence calculation based on text quality"""
        confidence = 0.5  # Base confidence
        
        # Length factor
        if len(text) > 100:
            confidence += 0.2
        if len(text) > 500:
            confidence += 0.1
        
        # Structure factor (simple heuristics)
        if any(word in text.lower() for word in ['requirements', 'need', 'want', 'should', 'must']):
            confidence += 0.1
        
        if any(word in text.lower() for word in ['system', 'application', 'platform', 'service']):
            confidence += 0.1
        
        # Punctuation factor
        if text.count('.') > 2:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract simple metadata from text"""
        return {
            "length": len(text),
            "word_count": len(text.split()),
            "sentence_count": text.count('.') + text.count('!') + text.count('?'),
            "has_technical_terms": any(word in text.lower() for word in [
                'api', 'database', 'server', 'client', 'frontend', 'backend'
            ])
        }
