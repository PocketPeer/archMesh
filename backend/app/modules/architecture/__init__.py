"""
Architecture Module - Simple & Modular

This module handles architecture generation with three simple components:
- ArchitectureGenerator: Generate architecture from requirements
- DiagramRenderer: Render C4 diagrams from architecture
- RecommendationEngine: Generate recommendations from architecture
"""

from .architecture_generator import ArchitectureGenerator
from .diagram_renderer import DiagramRenderer
from .recommendation_engine import RecommendationEngine

__all__ = [
    "ArchitectureGenerator",
    "DiagramRenderer", 
    "RecommendationEngine"
]
