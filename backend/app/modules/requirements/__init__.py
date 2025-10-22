"""
Requirements Module - Simple & Modular

This module handles requirements processing with three simple components:
- InputParser: Parse user input into structured data
- RequirementsExtractor: Extract requirements from parsed input
- RequirementsValidator: Validate extracted requirements
"""

from .input_parser import InputParser
from .requirements_extractor import RequirementsExtractor
from .requirements_validator import RequirementsValidator

__all__ = [
    "InputParser",
    "RequirementsExtractor", 
    "RequirementsValidator"
]
