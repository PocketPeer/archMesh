"""
Services package for ArchMesh PoC.

This package contains all service classes used in the ArchMesh system for
data processing, knowledge management, and external integrations.
"""

from .knowledge_base_service import KnowledgeBaseService

__all__ = [
    "KnowledgeBaseService",
]
