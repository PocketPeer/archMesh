"""
Simple tests for Requirements Module
"""

import pytest
from app.modules.requirements import InputParser, RequirementsExtractor, RequirementsValidator
from app.modules.requirements.models import InputType, ValidationStatus


class TestRequirementsModule:
    """Simple tests for Requirements Module components"""
    
    def test_input_parser_simple(self):
        """Test InputParser with simple input"""
        parser = InputParser()
        
        input_text = "We need a web application for managing customer orders. The system should be fast and secure."
        parsed = parser.parse(input_text)
        
        assert parsed.text == input_text
        assert parsed.input_type == InputType.TEXT
        assert parsed.confidence > 0.5
        assert "length" in parsed.metadata
    
    def test_input_parser_validation(self):
        """Test InputParser validation"""
        parser = InputParser()
        
        # Test too short input
        with pytest.raises(ValueError):
            parser.parse("short")
        
        # Test too long input
        long_input = "x" * 15000
        with pytest.raises(ValueError):
            parser.parse(long_input)
    
    def test_requirements_extractor_simple(self):
        """Test RequirementsExtractor with simple input"""
        parser = InputParser()
        extractor = RequirementsExtractor()
        
        input_text = "We need to increase sales by 20%. Users should be able to place orders online. The system must be secure and fast."
        parsed = parser.parse(input_text)
        requirements = extractor.extract(parsed)
        
        assert len(requirements.business_goals) > 0
        assert len(requirements.functional_requirements) > 0
        assert len(requirements.non_functional_requirements) > 0
    
    def test_requirements_validator_simple(self):
        """Test RequirementsValidator with simple requirements"""
        parser = InputParser()
        extractor = RequirementsExtractor()
        validator = RequirementsValidator()
        
        input_text = "We need to increase sales by 20%. Users should be able to place orders online. The system must be secure and fast. We have a budget of $50,000."
        parsed = parser.parse(input_text)
        requirements = extractor.extract(parsed)
        validation = validator.validate(requirements)
        
        assert validation.status in [ValidationStatus.VALID, ValidationStatus.WARNING]
        assert validation.score > 0.0
        assert isinstance(validation.issues, list)
        assert isinstance(validation.suggestions, list)
    
    def test_end_to_end_simple(self):
        """Test complete requirements processing pipeline"""
        parser = InputParser()
        extractor = RequirementsExtractor()
        validator = RequirementsValidator()
        
        # Simple requirements input
        input_text = """
        We need a customer management system for our business.
        Users should be able to create accounts and manage their profiles.
        The system must be secure and handle 1000 concurrent users.
        We have a budget of $100,000 and need it completed in 6 months.
        Our customers and administrators will use this system.
        """
        
        # Parse input
        parsed = parser.parse(input_text)
        assert parsed.confidence > 0.5
        
        # Extract requirements
        requirements = extractor.extract(parsed)
        
        # Check that we have some requirements extracted
        total_requirements = (
            len(requirements.business_goals) +
            len(requirements.functional_requirements) +
            len(requirements.non_functional_requirements) +
            len(requirements.constraints) +
            len(requirements.stakeholders)
        )
        assert total_requirements > 0, "Should extract at least some requirements"
        
        # Check specific types that should be present
        assert len(requirements.functional_requirements) > 0, "Should extract functional requirements"
        assert len(requirements.stakeholders) > 0, "Should extract stakeholders"
        
        # Validate requirements
        validation = validator.validate(requirements)
        assert validation.status in [ValidationStatus.VALID, ValidationStatus.WARNING]
        assert validation.score > 0.5
