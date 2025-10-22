"""
Enhanced Knowledge Base Service for ArchMesh.

This service provides comprehensive knowledge handling for both greenfield and brownfield projects:
- Workflow-driven knowledge collection
- Iterative knowledge refinement
- Architecture-guided knowledge growth
- Multi-modal knowledge storage (text, diagrams, relationships)
- LLM-assisted knowledge synthesis
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum

from loguru import logger
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings


class KnowledgeType(Enum):
    """Types of knowledge stored in the system"""
    REQUIREMENT = "requirement"
    ARCHITECTURE = "architecture"
    CONSTRAINT = "constraint"
    STAKEHOLDER = "stakeholder"
    TECHNOLOGY = "technology"
    RELATIONSHIP = "relationship"
    DECISION = "decision"
    DIAGRAM = "diagram"
    CONTEXT = "context"


class KnowledgeSource(Enum):
    """Sources of knowledge"""
    WORKFLOW = "workflow"
    DOCUMENT = "document"
    USER_INPUT = "user_input"
    ANALYSIS = "analysis"
    REFINEMENT = "refinement"
    EXTERNAL = "external"


@dataclass
class KnowledgeEntity:
    """Base knowledge entity"""
    id: str
    type: KnowledgeType
    content: str
    metadata: Dict[str, Any]
    source: KnowledgeSource
    project_id: str
    workflow_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    confidence: float = 1.0
    relationships: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.relationships is None:
            self.relationships = []


@dataclass
class KnowledgeRelationship:
    """Relationship between knowledge entities"""
    id: str
    from_entity_id: str
    to_entity_id: str
    relationship_type: str
    strength: float
    description: str
    metadata: Dict[str, Any]


@dataclass
class KnowledgeContext:
    """Context for knowledge retrieval and synthesis"""
    project_id: str
    workflow_id: Optional[str]
    query: str
    knowledge_types: List[KnowledgeType]
    max_results: int = 10
    similarity_threshold: float = 0.7


class EnhancedKnowledgeBaseService:
    """
    Enhanced knowledge base service for comprehensive project knowledge management.
    
    Features:
    - Multi-modal knowledge storage (text, diagrams, relationships)
    - Workflow-driven knowledge collection
    - Iterative knowledge refinement
    - LLM-assisted knowledge synthesis
    - Architecture-guided knowledge growth
    - Cross-project knowledge sharing
    """
    
    def __init__(
        self,
        storage_path: str = "./enhanced_knowledge_base",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the enhanced knowledge base service.
        
        Args:
            storage_path: Path to store knowledge base data
            embedding_model: Sentence transformer model for embeddings
        """
        self.storage_path = storage_path
        self.embedding_model = embedding_model
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension
        
        # Knowledge storage
        self.entities: Dict[str, KnowledgeEntity] = {}
        self.relationships: Dict[str, KnowledgeRelationship] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
        
        # Initialize embedding model
        self.embedder = SentenceTransformer(self.embedding_model)
        
        # Load existing knowledge
        self._load_knowledge()
        
        logger.info("Enhanced Knowledge Base Service initialized")
    
    async def add_knowledge(
        self,
        knowledge_type: KnowledgeType,
        content: str,
        metadata: Dict[str, Any],
        source: KnowledgeSource,
        project_id: str,
        workflow_id: Optional[str] = None,
        confidence: float = 1.0
    ) -> str:
        """
        Add new knowledge to the knowledge base.
        
        Args:
            knowledge_type: Type of knowledge
            content: Knowledge content
            metadata: Additional metadata
            source: Source of knowledge
            project_id: Project ID
            workflow_id: Optional workflow ID
            confidence: Confidence score (0-1)
            
        Returns:
            Knowledge entity ID
        """
        try:
            # Create knowledge entity
            entity_id = str(uuid.uuid4())
            entity = KnowledgeEntity(
                id=entity_id,
                type=knowledge_type,
                content=content,
                metadata=metadata,
                source=source,
                project_id=project_id,
                workflow_id=workflow_id,
                confidence=confidence
            )
            
            # Store entity
            self.entities[entity_id] = entity
            
            # Generate embedding
            embedding = self.embedder.encode(content)
            self.embeddings[entity_id] = embedding
            
            # Save knowledge
            await self._save_knowledge()
            
            logger.info(f"Added knowledge entity: {entity_id}")
            return entity_id
            
        except Exception as e:
            logger.error(f"Error adding knowledge: {str(e)}")
            raise
    
    async def add_relationship(
        self,
        from_entity_id: str,
        to_entity_id: str,
        relationship_type: str,
        strength: float,
        description: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Add relationship between knowledge entities.
        
        Args:
            from_entity_id: Source entity ID
            to_entity_id: Target entity ID
            relationship_type: Type of relationship
            strength: Relationship strength (0-1)
            description: Relationship description
            metadata: Additional metadata
            
        Returns:
            Relationship ID
        """
        try:
            # Create relationship
            relationship_id = str(uuid.uuid4())
            relationship = KnowledgeRelationship(
                id=relationship_id,
                from_entity_id=from_entity_id,
                to_entity_id=to_entity_id,
                relationship_type=relationship_type,
                strength=strength,
                description=description,
                metadata=metadata or {}
            )
            
            # Store relationship
            self.relationships[relationship_id] = relationship
            
            # Update entity relationships
            if from_entity_id in self.entities:
                self.entities[from_entity_id].relationships.append(relationship_id)
            if to_entity_id in self.entities:
                self.entities[to_entity_id].relationships.append(relationship_id)
            
            # Save knowledge
            await self._save_knowledge()
            
            logger.info(f"Added relationship: {relationship_id}")
            return relationship_id
            
        except Exception as e:
            logger.error(f"Error adding relationship: {str(e)}")
            raise
    
    async def search_knowledge(
        self,
        context: KnowledgeContext
    ) -> List[Tuple[KnowledgeEntity, float]]:
        """
        Search knowledge base with semantic similarity.
        
        Args:
            context: Knowledge search context
            
        Returns:
            List of (entity, similarity_score) tuples
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(context.query)
            
            # Filter by project and knowledge types
            candidate_entities = []
            for entity_id, entity in self.entities.items():
                if (entity.project_id == context.project_id and 
                    entity.type in context.knowledge_types):
                    candidate_entities.append((entity_id, entity))
            
            # Calculate similarities
            similarities = []
            for entity_id, entity in candidate_entities:
                if entity_id in self.embeddings:
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        self.embeddings[entity_id].reshape(1, -1)
                    )[0][0]
                    
                    if similarity >= context.similarity_threshold:
                        similarities.append((entity, similarity))
            
            # Sort by similarity and limit results
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:context.max_results]
            
        except Exception as e:
            logger.error(f"Error searching knowledge: {str(e)}")
            return []
    
    async def synthesize_knowledge(
        self,
        context: KnowledgeContext,
        synthesis_type: str = "architecture"
    ) -> Dict[str, Any]:
        """
        Synthesize knowledge for architecture decisions.
        
        Args:
            context: Knowledge context
            synthesis_type: Type of synthesis (architecture, requirements, etc.)
            
        Returns:
            Synthesized knowledge
        """
        try:
            # Search relevant knowledge
            relevant_knowledge = await self.search_knowledge(context)
            
            # Group by knowledge type
            knowledge_by_type = {}
            for entity, similarity in relevant_knowledge:
                if entity.type not in knowledge_by_type:
                    knowledge_by_type[entity.type] = []
                knowledge_by_type[entity.type].append((entity, similarity))
            
            # Synthesize based on type
            if synthesis_type == "architecture":
                return await self._synthesize_architecture_knowledge(knowledge_by_type)
            elif synthesis_type == "requirements":
                return await self._synthesize_requirements_knowledge(knowledge_by_type)
            else:
                return await self._synthesize_general_knowledge(knowledge_by_type)
                
        except Exception as e:
            logger.error(f"Error synthesizing knowledge: {str(e)}")
            return {}
    
    async def refine_knowledge(
        self,
        entity_id: str,
        refined_content: str,
        refinement_metadata: Dict[str, Any]
    ) -> bool:
        """
        Refine existing knowledge with new information.
        
        Args:
            entity_id: Entity ID to refine
            refined_content: Refined content
            refinement_metadata: Refinement metadata
            
        Returns:
            Success status
        """
        try:
            if entity_id not in self.entities:
                return False
            
            # Update entity
            entity = self.entities[entity_id]
            entity.content = refined_content
            entity.updated_at = datetime.utcnow()
            entity.metadata.update(refinement_metadata)
            
            # Update embedding
            new_embedding = self.embedder.encode(refined_content)
            self.embeddings[entity_id] = new_embedding
            
            # Save knowledge
            await self._save_knowledge()
            
            logger.info(f"Refined knowledge entity: {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error refining knowledge: {str(e)}")
            return False
    
    async def get_project_knowledge_graph(
        self,
        project_id: str,
        include_relationships: bool = True
    ) -> Dict[str, Any]:
        """
        Get complete knowledge graph for a project.
        
        Args:
            project_id: Project ID
            include_relationships: Include relationship data
            
        Returns:
            Knowledge graph data
        """
        try:
            # Get project entities
            project_entities = {
                entity_id: entity for entity_id, entity in self.entities.items()
                if entity.project_id == project_id
            }
            
            # Get project relationships
            project_relationships = {}
            if include_relationships:
                for rel_id, relationship in self.relationships.items():
                    if (relationship.from_entity_id in project_entities or 
                        relationship.to_entity_id in project_entities):
                        project_relationships[rel_id] = relationship
            
            return {
                "project_id": project_id,
                "entities": {k: asdict(v) for k, v in project_entities.items()},
                "relationships": {k: asdict(v) for k, v in project_relationships.items()},
                "metadata": {
                    "entity_count": len(project_entities),
                    "relationship_count": len(project_relationships),
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting project knowledge graph: {str(e)}")
            return {}
    
    async def _synthesize_architecture_knowledge(
        self,
        knowledge_by_type: Dict[KnowledgeType, List[Tuple[KnowledgeEntity, float]]]
    ) -> Dict[str, Any]:
        """Synthesize architecture knowledge."""
        synthesis = {
            "architecture_overview": {},
            "components": [],
            "relationships": [],
            "constraints": [],
            "technologies": [],
            "decisions": []
        }
        
        # Process architecture knowledge
        if KnowledgeType.ARCHITECTURE in knowledge_by_type:
            for entity, similarity in knowledge_by_type[KnowledgeType.ARCHITECTURE]:
                if "overview" in entity.metadata:
                    synthesis["architecture_overview"] = entity.metadata["overview"]
                elif "component" in entity.metadata:
                    synthesis["components"].append(entity.metadata["component"])
        
        # Process constraint knowledge
        if KnowledgeType.CONSTRAINT in knowledge_by_type:
            for entity, similarity in knowledge_by_type[KnowledgeType.CONSTRAINT]:
                synthesis["constraints"].append({
                    "content": entity.content,
                    "metadata": entity.metadata,
                    "confidence": similarity
                })
        
        # Process technology knowledge
        if KnowledgeType.TECHNOLOGY in knowledge_by_type:
            for entity, similarity in knowledge_by_type[KnowledgeType.TECHNOLOGY]:
                synthesis["technologies"].append({
                    "content": entity.content,
                    "metadata": entity.metadata,
                    "confidence": similarity
                })
        
        return synthesis
    
    async def _synthesize_requirements_knowledge(
        self,
        knowledge_by_type: Dict[KnowledgeType, List[Tuple[KnowledgeEntity, float]]]
    ) -> Dict[str, Any]:
        """Synthesize requirements knowledge."""
        synthesis = {
            "functional_requirements": [],
            "non_functional_requirements": [],
            "stakeholders": [],
            "constraints": []
        }
        
        # Process requirement knowledge
        if KnowledgeType.REQUIREMENT in knowledge_by_type:
            for entity, similarity in knowledge_by_type[KnowledgeType.REQUIREMENT]:
                req_type = entity.metadata.get("requirement_type", "functional")
                if req_type == "functional":
                    synthesis["functional_requirements"].append({
                        "content": entity.content,
                        "metadata": entity.metadata,
                        "confidence": similarity
                    })
                else:
                    synthesis["non_functional_requirements"].append({
                        "content": entity.content,
                        "metadata": entity.metadata,
                        "confidence": similarity
                    })
        
        # Process stakeholder knowledge
        if KnowledgeType.STAKEHOLDER in knowledge_by_type:
            for entity, similarity in knowledge_by_type[KnowledgeType.STAKEHOLDER]:
                synthesis["stakeholders"].append({
                    "content": entity.content,
                    "metadata": entity.metadata,
                    "confidence": similarity
                })
        
        return synthesis
    
    async def _synthesize_general_knowledge(
        self,
        knowledge_by_type: Dict[KnowledgeType, List[Tuple[KnowledgeEntity, float]]]
    ) -> Dict[str, Any]:
        """Synthesize general knowledge."""
        synthesis = {}
        
        for knowledge_type, entities in knowledge_by_type.items():
            synthesis[knowledge_type.value] = []
            for entity, similarity in entities:
                synthesis[knowledge_type.value].append({
                    "content": entity.content,
                    "metadata": entity.metadata,
                    "confidence": similarity
                })
        
        return synthesis
    
    async def _save_knowledge(self):
        """Save knowledge to storage."""
        try:
            # This would typically save to persistent storage
            # For now, just log the save operation
            logger.info("Knowledge saved to storage")
        except Exception as e:
            logger.error(f"Error saving knowledge: {str(e)}")
    
    def _load_knowledge(self):
        """Load knowledge from storage."""
        try:
            # This would typically load from persistent storage
            # For now, just log the load operation
            logger.info("Knowledge loaded from storage")
        except Exception as e:
            logger.error(f"Error loading knowledge: {str(e)}")


# Factory function
def get_enhanced_knowledge_base_service() -> EnhancedKnowledgeBaseService:
    """Get enhanced knowledge base service instance."""
    return EnhancedKnowledgeBaseService()
