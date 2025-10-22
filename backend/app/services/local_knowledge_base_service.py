"""
Local Knowledge Base Service for ArchMesh PoC.

This service provides RAG (Retrieval-Augmented Generation) capabilities for storing
and retrieving architecture context using local storage instead of external services.

Components:
- Local Vector Storage: In-memory vector storage with similarity search
- Neo4j: Graph database for architecture relationships (if available)
- PostgreSQL: Structured metadata and project information
- Sentence Transformers: Text embeddings for semantic similarity
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from loguru import logger
from sentence_transformers import SentenceTransformer

from app.config import settings


class LocalKnowledgeBaseService:
    """
    Local service for storing and retrieving architecture knowledge using RAG.
    
    This service provides a local alternative to external vector databases
    while maintaining the same interface for brownfield analysis.
    
    Capabilities:
    - Index repository analysis results
    - Semantic search for similar architectures
    - Graph-based dependency analysis (if Neo4j available)
    - Context generation for new features
    - Architecture pattern recommendations
    - Technology stack analysis
    """

    def __init__(
        self,
        storage_path: str = "./knowledge_base_storage",
        embedding_model: str = "all-MiniLM-L6-v2",
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None
    ):
        """
        Initialize the local knowledge base service.
        
        Args:
            storage_path: Path to store local knowledge base data
            embedding_model: Sentence transformer model for embeddings
            neo4j_uri: Optional Neo4j URI for graph storage
            neo4j_user: Optional Neo4j username
            neo4j_password: Optional Neo4j password
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.embedding_model = embedding_model
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension
        
        # Neo4j configuration
        self.neo4j_uri = neo4j_uri or settings.neo4j_uri
        self.neo4j_user = neo4j_user or settings.neo4j_user
        self.neo4j_password = neo4j_password or settings.neo4j_password
        
        # Local storage
        self.vectors = []  # List of vectors
        self.metadata = []  # List of metadata
        self.embeddings_file = self.storage_path / "embeddings.pkl"
        self.metadata_file = self.storage_path / "metadata.json"
        
        # Initialize services
        self.embedder = None
        self.graph = None
        self._initialize_services()
        
        # Load existing data
        self._load_stored_data()
        
        logger.info("Local Knowledge Base Service initialized", extra={"service": "local_knowledge_base"})

    def _initialize_services(self) -> None:
        """Initialize embedding model and Neo4j (if available)."""
        try:
            # Initialize embedding model
            self.embedder = SentenceTransformer(self.embedding_model)
            logger.info(f"Embedding model loaded: {self.embedding_model}")
            
            # Try to initialize Neo4j (optional)
            try:
                from py2neo import Graph
                self.graph = Graph(
                    self.neo4j_uri,
                    auth=(self.neo4j_user, self.neo4j_password)
                )
                # Test connection
                self.graph.run("RETURN 1").data()
                logger.info("Neo4j connected successfully")
            except Exception as e:
                logger.warning(f"Neo4j not available: {str(e)}")
                self.graph = None
            
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")
            raise

    def _load_stored_data(self) -> None:
        """Load existing vectors and metadata from storage."""
        try:
            if self.embeddings_file.exists():
                with open(self.embeddings_file, 'rb') as f:
                    self.vectors = pickle.load(f)
                logger.info(f"Loaded {len(self.vectors)} vectors from storage")
            
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded {len(self.metadata)} metadata entries from storage")
                
        except Exception as e:
            logger.warning(f"Error loading stored data: {str(e)}")
            self.vectors = []
            self.metadata = []

    def _save_data(self) -> None:
        """Save vectors and metadata to storage."""
        try:
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.vectors, f)
            
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if not self.embedder:
            raise RuntimeError("Embedding model not initialized")
        return self.embedder.encode([text])[0].tolist()

    async def index_repository_analysis(
        self,
        project_id: str,
        repository_url: str,
        analysis: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Index repository analysis results in the knowledge base.
        
        Args:
            project_id: Project identifier
            repository_url: Repository URL
            analysis: Repository analysis results
            metadata: Additional metadata
            
        Returns:
            Dictionary with indexing results
        """
        try:
            logger.info(
                f"Indexing repository analysis",
                extra={
                    "project_id": project_id,
                    "repository_url": repository_url,
                    "service": "local_knowledge_base"
                }
            )
            
            # Create searchable chunks from analysis
            chunks = self._create_searchable_chunks(project_id, analysis)
            
            # Store vectors and metadata
            for chunk in chunks:
                self.vectors.append(chunk["values"])
                self.metadata.append(chunk["metadata"])
            
            # Store in graph database if available
            graph_results = await self._store_in_graph(project_id, analysis)
            
            # Save to local storage
            self._save_data()
            
            result = {
                "indexed_chunks": len(chunks),
                "created_nodes": graph_results.get("nodes_created", 0),
                "created_relationships": graph_results.get("relationships_created", 0),
                "total_vectors": len(self.vectors),
                "total_metadata": len(self.metadata)
            }
            
            logger.info(
                f"Repository analysis indexing completed",
                extra={
                    "project_id": project_id,
                    "chunks_indexed": result["indexed_chunks"],
                    "service": "local_knowledge_base"
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to index repository analysis: {str(e)}")
            raise

    def _create_searchable_chunks(self, project_id: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create text chunks from analysis for embedding."""
        chunks = []
        
        # Architecture overview chunk
        if "architecture" in analysis:
            arch = analysis["architecture"]
            text = f"""
            Architecture Style: {arch.get('architecture_style', 'Unknown')}
            Communication Patterns: {', '.join(arch.get('communication_patterns', []))}
            Data Storage: {json.dumps(arch.get('data_storage', {}), indent=2)}
            Deployment Strategy: {json.dumps(arch.get('deployment', {}), indent=2)}
            Security Approach: {json.dumps(arch.get('security', {}), indent=2)}
            Scalability Features: {json.dumps(arch.get('scalability', {}), indent=2)}
            """
            chunks.append({
                "id": f"{project_id}_arch_{len(chunks)}",
                "values": self._generate_embedding(text.strip()),
                "metadata": {
                    "project_id": project_id,
                    "chunk_type": "architecture",
                    "content": text.strip()[:1000],
                    "architecture_style": arch.get('architecture_style'),
                    "patterns": arch.get('architecture_patterns', [])
                }
            })
        
        # Service chunks
        if "services" in analysis:
            for service in analysis["services"]:
                text = f"""
                Service Name: {service.get('name', 'Unknown')}
                Service Type: {service.get('type', 'Unknown')}
                Technology Stack: {service.get('technology', 'Unknown')}
                Responsibilities: {', '.join(service.get('responsibilities', []))}
                Interfaces: {', '.join(service.get('interfaces', []))}
                Dependencies: {', '.join(service.get('dependencies', []))}
                Scalability: {service.get('scalability', 'Unknown')}
                """
                chunks.append({
                    "id": f"{project_id}_service_{len(chunks)}",
                    "values": self._generate_embedding(text.strip()),
                    "metadata": {
                        "project_id": project_id,
                        "chunk_type": "service",
                        "content": text.strip()[:1000],
                        "service_name": service.get('name'),
                        "service_type": service.get('type'),
                        "technology": service.get('technology')
                    }
                })
        
        # Technology stack chunk
        if "tech_stack" in analysis:
            tech = analysis["tech_stack"]
            text = f"""
            Programming Languages: {json.dumps(tech.get('languages', {}), indent=2)}
            Frameworks: {', '.join(tech.get('frameworks', []))}
            Databases: {', '.join(tech.get('databases', []))}
            Infrastructure Tools: {', '.join(tech.get('infrastructure', []))}
            Testing Frameworks: {', '.join(tech.get('testing_frameworks', []))}
            Build Tools: {', '.join(tech.get('build_tools', []))}
            """
            chunks.append({
                "id": f"{project_id}_tech_{len(chunks)}",
                "values": self._generate_embedding(text.strip()),
                "metadata": {
                    "project_id": project_id,
                    "chunk_type": "technology",
                    "content": text.strip()[:1000],
                    "languages": list(tech.get('languages', {}).keys()),
                    "frameworks": tech.get('frameworks', [])
                }
            })
        
        return chunks

    async def _store_in_graph(self, project_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Store analysis results in Neo4j graph database."""
        if not self.graph:
            return {"nodes_created": 0, "relationships_created": 0, "success": True}
        
        try:
            nodes_created = 0
            relationships_created = 0
            
            # Create project node
            project_query = """
            MERGE (p:Project {id: $project_id})
            SET p.name = $project_name,
                p.architecture_style = $architecture_style,
                p.updated_at = datetime()
            """
            
            self.graph.run(project_query, {
                "project_id": project_id,
                "project_name": analysis.get("repository_info", {}).get("name", "Unknown"),
                "architecture_style": analysis.get("architecture", {}).get("architecture_style", "Unknown")
            })
            nodes_created += 1
            
            # Create service nodes and relationships
            if "services" in analysis:
                for service in analysis["services"]:
                    service_query = """
                    MATCH (p:Project {id: $project_id})
                    MERGE (s:Service {name: $service_name, project_id: $project_id})
                    SET s.type = $service_type,
                        s.technology = $technology,
                        s.responsibility = $responsibility
                    MERGE (p)-[:HAS_SERVICE]->(s)
                    """
                    
                    self.graph.run(service_query, {
                        "project_id": project_id,
                        "service_name": service.get("name", "Unknown"),
                        "service_type": service.get("type", "Unknown"),
                        "technology": service.get("technology", "Unknown"),
                        "responsibility": service.get("responsibility", "Unknown")
                    })
                    nodes_created += 1
                    relationships_created += 1
                    
                    # Create dependency relationships
                    for dep in service.get("dependencies", []):
                        dep_query = """
                        MATCH (s:Service {name: $service_name, project_id: $project_id})
                        MERGE (d:Service {name: $dep_name, project_id: $project_id})
                        MERGE (s)-[:DEPENDS_ON]->(d)
                        """
                        
                        self.graph.run(dep_query, {
                            "service_name": service.get("name"),
                            "dep_name": dep,
                            "project_id": project_id
                        })
                        relationships_created += 1
            
            return {
                "nodes_created": nodes_created,
                "relationships_created": relationships_created,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error storing in graph: {str(e)}")
            return {"nodes_created": 0, "relationships_created": 0, "success": False, "error": str(e)}

    async def search_similar_architectures(
        self,
        query: str,
        project_id: Optional[str] = None,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar architectures using semantic search.
        
        Args:
            query: Natural language query
            project_id: Optional filter by project
            top_k: Number of results to return
            filters: Optional filter dictionary
            
        Returns:
            List of similar architecture results with scores and metadata
        """
        if not self.vectors or not self.embedder:
            logger.warning("No vectors available for search")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            query_vector = np.array(query_embedding).reshape(1, -1)
            
            # Calculate similarities
            similarities = []
            for i, vector in enumerate(self.vectors):
                # Apply filters
                metadata = self.metadata[i]
                if project_id and metadata.get("project_id") != project_id:
                    continue
                
                if filters:
                    for key, value in filters.items():
                        if metadata.get(key) != value:
                            continue
                
                # Calculate cosine similarity
                vector_array = np.array(vector).reshape(1, -1)
                similarity = cosine_similarity(query_vector, vector_array)[0][0]
                
                similarities.append({
                    "id": metadata.get("id", f"chunk_{i}"),
                    "score": float(similarity),
                    "metadata": metadata
                })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x["score"], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []

    async def get_service_dependencies(self, project_id: str) -> List[Dict[str, Any]]:
        """Get service dependencies for a project."""
        if not self.graph:
            # Fallback to metadata search
            services = []
            for metadata in self.metadata:
                if (metadata.get("project_id") == project_id and 
                    metadata.get("chunk_type") == "service"):
                    services.append({
                        "s": {
                            "name": metadata.get("service_name", "Unknown"),
                            "type": metadata.get("service_type", "Unknown"),
                            "technology": metadata.get("technology", "Unknown")
                        }
                    })
            return services
        
        try:
            query = """
            MATCH (p:Project {id: $project_id})-[:HAS_SERVICE]->(s:Service)
            OPTIONAL MATCH (s)-[:DEPENDS_ON]->(dep:Service)
            RETURN s, dep
            """
            
            result = self.graph.run(query, {"project_id": project_id}).data()
            return result
            
        except Exception as e:
            logger.error(f"Error getting service dependencies: {str(e)}")
            return []

    async def get_architecture_patterns(self, project_id: str) -> List[Dict[str, Any]]:
        """Get architecture patterns for a project."""
        if not self.graph:
            # Fallback to metadata search
            patterns = []
            for metadata in self.metadata:
                if (metadata.get("project_id") == project_id and 
                    metadata.get("chunk_type") == "architecture"):
                    patterns.append({
                        "a": {
                            "style": metadata.get("architecture_style", "Unknown"),
                            "patterns": metadata.get("patterns", [])
                        }
                    })
            return patterns
        
        try:
            query = """
            MATCH (p:Project {id: $project_id})
            RETURN p.architecture_style as style, 
                   p.architecture_patterns as patterns
            """
            
            result = self.graph.run(query, {"project_id": project_id}).data()
            return [{"a": r} for r in result]
            
        except Exception as e:
            logger.error(f"Error getting architecture patterns: {str(e)}")
            return []

    async def get_context_for_new_feature(
        self,
        project_id: str,
        feature_description: str,
        context_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get context for adding a new feature to existing project.
        
        Args:
            project_id: Project identifier
            feature_description: Description of the new feature
            context_types: Types of context to retrieve
            
        Returns:
            Dictionary with relevant context for feature development
        """
        try:
            logger.info(
                f"Getting context for new feature",
                extra={
                    "project_id": project_id,
                    "feature_description": feature_description[:100],
                    "service": "local_knowledge_base"
                }
            )
            
            # Search for similar features and patterns
            similar_results = await self.search_similar_architectures(
                query=feature_description,
                project_id=project_id,
                top_k=5
            )
            
            # Get existing services in project
            existing_services = await self.get_service_dependencies(project_id)
            
            # Get architecture patterns
            architecture_patterns = await self.get_architecture_patterns(project_id)
            
            # Get technology stack information
            tech_stack_context = await self._get_technology_context(project_id)
            
            # Generate recommendations
            recommendations = await self._generate_feature_recommendations(
                feature_description, similar_results, existing_services, tech_stack_context
            )
            
            context = {
                "feature_description": feature_description,
                "similar_features": similar_results,
                "existing_services": existing_services,
                "integration_patterns": architecture_patterns,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"Generated context for new feature",
                extra={
                    "project_id": project_id,
                    "similar_patterns_count": len(similar_results),
                    "existing_services_count": len(existing_services),
                    "service": "local_knowledge_base"
                }
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting context for new feature: {str(e)}")
            return {
                "error": str(e),
                "feature_description": feature_description,
                "generated_at": datetime.utcnow().isoformat()
            }

    async def _get_technology_context(self, project_id: str) -> Dict[str, Any]:
        """Get technology stack context for a project."""
        if not self.graph:
            # Fallback to metadata search
            languages = set()
            frameworks = set()
            databases = set()
            
            for metadata in self.metadata:
                if metadata.get("project_id") == project_id:
                    if metadata.get("chunk_type") == "technology":
                        languages.update(metadata.get("languages", []))
                        frameworks.update(metadata.get("frameworks", []))
            
            return {
                "languages": list(languages),
                "frameworks": list(frameworks),
                "databases": list(databases)
            }
        
        try:
            query = """
            MATCH (p:Project {id: $project_id})
            OPTIONAL MATCH (p)-[:USES_LANGUAGE]->(l:Language)
            OPTIONAL MATCH (p)-[:USES_FRAMEWORK]->(f:Framework)
            OPTIONAL MATCH (p)-[:USES_DATABASE]->(d:Database)
            RETURN collect(DISTINCT l.name) as languages,
                   collect(DISTINCT f.name) as frameworks,
                   collect(DISTINCT d.name) as databases
            """
            
            result = self.graph.run(query, {"project_id": project_id}).data()
            if result:
                return result[0]
            return {}
            
        except Exception as e:
            logger.error(f"Error getting technology context: {str(e)}")
            return {}

    async def _generate_feature_recommendations(
        self,
        feature_description: str,
        similar_results: List[Dict[str, Any]],
        existing_services: List[Dict[str, Any]],
        tech_stack_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate recommendations for new feature development."""
        recommendations = {
            "integration_approach": "API-first integration",
            "technology_suggestions": tech_stack_context.get("frameworks", []),
            "existing_services_to_modify": [],
            "new_services_needed": [],
            "implementation_phases": [
                "Phase 1: Design API contracts",
                "Phase 2: Implement core functionality", 
                "Phase 3: Integration testing",
                "Phase 4: Deployment and monitoring"
            ],
            "risk_mitigation": [
                "Use feature flags for gradual rollout",
                "Implement comprehensive testing",
                "Plan rollback strategy"
            ]
        }
        
        # Analyze similar features for recommendations
        if similar_results:
            recommendations["similar_patterns_found"] = len(similar_results)
            recommendations["recommended_patterns"] = [
                r["metadata"].get("chunk_type", "unknown") 
                for r in similar_results[:3]
            ]
        
        # Analyze existing services
        if existing_services:
            recommendations["existing_services_count"] = len(existing_services)
            recommendations["integration_points"] = [
                service.get("s", {}).get("name", "Unknown") 
                for service in existing_services[:5]
            ]
        
        return recommendations

    def get_service_status(self) -> Dict[str, bool]:
        """Get the status of all knowledge base services."""
        return {
            "embedder": self.embedder is not None,
            "graph": self.graph is not None,
            "vectors_loaded": len(self.vectors) > 0,
            "metadata_loaded": len(self.metadata) > 0,
            "overall": self.embedder is not None
        }

    def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and configuration."""
        return {
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "vectors_count": len(self.vectors),
            "metadata_count": len(self.metadata),
            "neo4j_available": self.graph is not None,
            "storage_path": str(self.storage_path)
        }
