"""
Requirements Agent for ArchMesh PoC.

This agent is responsible for parsing business requirements documents and extracting
structured requirements, generating clarifying questions, and identifying gaps.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from app.agents.base_agent import BaseAgent


class RequirementsAgent(BaseAgent):
    """
    Agent responsible for parsing business requirements documents.
    
    Capabilities:
    - Parse text files, PowerPoint (future), PDF (future)
    - Extract structured requirements
    - Generate clarifying questions
    - Identify gaps and ambiguities
    - Provide confidence scoring
    """

    def __init__(self):
        """
        Initialize the Requirements Agent.
        
        Uses Claude Sonnet for consistent and accurate requirements extraction
        with lower temperature for more deterministic results.
        """
        super().__init__(
            agent_type="requirements_extractor",
            agent_version="1.0.0",
            llm_provider="anthropic",
            llm_model="claude-3-5-sonnet-20241022",
            temperature=0.5,  # Lower for more consistent extraction
            max_retries=3,
            timeout_seconds=120,
            max_tokens=4000
        )
        
        # Supported file extensions
        self.supported_extensions = {'.txt', '.md', '.rst'}
        
        logger.info("Requirements Agent initialized", extra={"agent_type": "requirements_extractor"})

    def get_system_prompt(self) -> str:
        """
        Return the system prompt for requirements extraction.
        
        Returns:
            System prompt string with detailed instructions for requirements analysis
        """
        return """You are an expert business analyst and requirements engineer with 15+ years of experience in software development and enterprise architecture.

Your responsibilities:
1. Parse business requirements documents thoroughly and systematically
2. Extract and structure requirements into clear, actionable categories:
   - Business goals and objectives
   - Functional requirements (what the system should do)
   - Non-functional requirements (how the system should perform)
   - Constraints (budget, timeline, technology, regulatory)
   - Stakeholders and their specific concerns
3. Identify ambiguities, gaps, and missing information
4. Generate 5-10 clarifying questions, prioritized by importance and impact
5. Provide a confidence score (0.0-1.0) based on document clarity and completeness
6. Output structured JSON following the exact schema provided

Guidelines:
- Be thorough and systematic in your analysis
- Ask insightful, specific questions that will help clarify requirements
- Focus on business value and technical feasibility
- Consider scalability, security, and maintainability
- Identify potential risks and dependencies
- Ensure requirements are testable and measurable

Always output valid JSON wrapped in ```json code blocks. Be precise and comprehensive."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse requirements from documents and extract structured information.
        
        Args:
            input_data: Dictionary containing:
                - document_path: Path to the document file
                - project_context: Optional project context information
                - domain: Project domain (cloud-native, data-platform, enterprise)
                - session_id: Optional workflow session ID for logging
                
        Returns:
            Dictionary containing:
                - structured_requirements: Organized requirements data
                - clarification_questions: List of questions for stakeholders
                - identified_gaps: List of missing or unclear information
                - confidence_score: Confidence in the extraction (0.0-1.0)
                - metadata: Additional processing information
                
        Raises:
            FileNotFoundError: If document file doesn't exist
            ValueError: If document format is not supported
            Exception: For other processing errors
        """
        try:
            # Validate input
            if "document_path" not in input_data:
                raise ValueError("document_path is required in input_data")
            
            document_path = input_data["document_path"]
            project_context = input_data.get("project_context", "")
            domain = input_data.get("domain", "cloud-native")
            session_id = input_data.get("session_id")
            
            logger.info(
                f"Starting requirements extraction",
                extra={
                    "agent_type": self.agent_type,
                    "document_path": document_path,
                    "domain": domain,
                    "session_id": session_id,
                }
            )
            
            # 1. Read and validate document
            content = await self._read_document(document_path)
            
            if not content.strip():
                raise ValueError(f"Document {document_path} is empty or contains no readable content")
            
            # 2. Build comprehensive extraction prompt
            prompt = self._build_extraction_prompt(content, project_context, domain)
            
            # 3. Call LLM for requirements extraction
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            response = await self._call_llm(messages)
            
            # 4. Parse and validate response
            structured_data = self._parse_json_response(response)
            
            # 5. Validate and enhance the extracted data
            enhanced_data = self._validate_and_enhance_extraction(structured_data, content)
            
            # 6. Add metadata
            enhanced_data["metadata"] = {
                "document_path": document_path,
                "document_size": len(content),
                "domain": domain,
                "extraction_timestamp": self.start_time.isoformat() if self.start_time else None,
                "agent_version": self.agent_version,
                "processing_notes": self._generate_processing_notes(content, enhanced_data)
            }
            
            logger.info(
                f"Requirements extraction completed successfully",
                extra={
                    "agent_type": self.agent_type,
                    "document_path": document_path,
                    "confidence_score": enhanced_data.get("confidence_score", 0.0),
                    "questions_count": len(enhanced_data.get("clarification_questions", [])),
                    "gaps_count": len(enhanced_data.get("identified_gaps", [])),
                }
            )
            
            return enhanced_data
            
        except Exception as e:
            logger.error(
                f"Requirements extraction failed: {str(e)}",
                extra={
                    "agent_type": self.agent_type,
                    "document_path": input_data.get("document_path"),
                    "error": str(e),
                }
            )
            raise

    async def _read_document(self, file_path: str) -> str:
        """
        Read document content from file.
        
        Currently supports:
        - .txt files (plain text)
        - .md files (markdown)
        - .rst files (reStructuredText)
        
        Future support planned for:
        - .pdf files (PDF documents)
        - .pptx files (PowerPoint presentations)
        - .docx files (Word documents)
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Document content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
            Exception: For other file reading errors
        """
        try:
            path = Path(file_path)
            
            # Check if file exists
            if not path.exists():
                raise FileNotFoundError(f"Document file not found: {file_path}")
            
            # Check file extension
            if path.suffix.lower() not in self.supported_extensions:
                raise ValueError(
                    f"Unsupported file format: {path.suffix}. "
                    f"Supported formats: {', '.join(self.supported_extensions)}"
                )
            
            # Read file content
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            logger.debug(
                f"Document read successfully",
                extra={
                    "file_path": file_path,
                    "file_size": len(content),
                    "file_extension": path.suffix,
                }
            )
            
            return content
            
        except UnicodeDecodeError as e:
            # Try with different encoding
            try:
                with open(path, 'r', encoding='latin-1') as file:
                    content = file.read()
                logger.warning(f"Document read with latin-1 encoding: {file_path}")
                return content
            except Exception:
                raise ValueError(f"Could not decode document file: {file_path}. Error: {str(e)}")
        
        except Exception as e:
            raise Exception(f"Failed to read document {file_path}: {str(e)}")

    def _build_extraction_prompt(
        self,
        content: str,
        context: str,
        domain: str
    ) -> str:
        """
        Build comprehensive extraction prompt for the LLM.
        
        Args:
            content: Document content
            context: Additional project context
            domain: Project domain
            
        Returns:
            Formatted prompt string
        """
        # Truncate content if too long (keep first 8000 characters)
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n\n[Document truncated for processing...]"
        
        prompt = f"""Analyze the following business requirements document and extract structured requirements:

PROJECT CONTEXT:
Domain: {domain}
{f"Additional Context: {context}" if context else "No additional context provided"}

DOCUMENT CONTENT:
\"\"\"
{content}
\"\"\"

Please extract and structure the information according to this JSON schema:

{{
  "structured_requirements": {{
    "business_goals": [
      "Clear, specific business objectives and goals"
    ],
    "functional_requirements": [
      "Specific features and functionality the system must provide"
    ],
    "non_functional_requirements": {{
      "performance": ["Performance requirements (response time, throughput, etc.)"],
      "security": ["Security requirements (authentication, authorization, data protection)"],
      "scalability": ["Scalability requirements (user load, data volume, growth)"],
      "reliability": ["Reliability requirements (uptime, fault tolerance, backup)"],
      "maintainability": ["Maintainability requirements (code quality, documentation, testing)"],
      "usability": ["Usability requirements (user interface, accessibility, user experience)"],
      "compliance": ["Compliance requirements (regulatory, legal, industry standards)"]
    }},
    "constraints": [
      "Technical, business, or resource constraints"
    ],
    "stakeholders": [
      {{
        "name": "Stakeholder name or role",
        "role": "Specific role or title",
        "concerns": ["Primary concerns and interests"],
        "influence": "high|medium|low"
      }}
    ]
  }},
  "clarification_questions": [
    {{
      "question": "Specific question to clarify requirements",
      "category": "business|technical|constraint|stakeholder",
      "priority": "high|medium|low",
      "rationale": "Why this question is important"
    }}
  ],
  "identified_gaps": [
    "Missing or unclear information that needs to be addressed"
  ],
  "confidence_score": 0.85
}}

INSTRUCTIONS:
1. Be thorough and systematic in your analysis
2. Extract ALL relevant requirements, even if implicit
3. Generate 5-10 high-quality clarifying questions
4. Identify gaps and ambiguities
5. Provide a realistic confidence score (0.0-1.0)
6. Ensure all requirements are specific, measurable, and actionable
7. Consider the {domain} domain context in your analysis

Output ONLY the JSON, wrapped in ```json code blocks. Be precise and comprehensive."""

        return prompt

    def _validate_and_enhance_extraction(
        self,
        extracted_data: Dict[str, Any],
        original_content: str
    ) -> Dict[str, Any]:
        """
        Validate and enhance the extracted requirements data.
        
        Args:
            extracted_data: Raw extracted data from LLM
            original_content: Original document content
            
        Returns:
            Validated and enhanced data
        """
        try:
            # Ensure required fields exist
            if "structured_requirements" not in extracted_data:
                extracted_data["structured_requirements"] = {}
            
            if "clarification_questions" not in extracted_data:
                extracted_data["clarification_questions"] = []
            
            if "identified_gaps" not in extracted_data:
                extracted_data["identified_gaps"] = []
            
            if "confidence_score" not in extracted_data:
                extracted_data["confidence_score"] = 0.5
            
            # Validate confidence score
            confidence = extracted_data["confidence_score"]
            if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
                extracted_data["confidence_score"] = 0.5
            
            # Ensure structured_requirements has required sections
            req = extracted_data["structured_requirements"]
            required_sections = [
                "business_goals", "functional_requirements", "non_functional_requirements",
                "constraints", "stakeholders"
            ]
            
            for section in required_sections:
                if section not in req:
                    req[section] = [] if section != "non_functional_requirements" else {}
            
            # Ensure non_functional_requirements has required categories
            nfr = req["non_functional_requirements"]
            nfr_categories = [
                "performance", "security", "scalability", "reliability",
                "maintainability", "usability", "compliance"
            ]
            
            for category in nfr_categories:
                if category not in nfr:
                    nfr[category] = []
            
            # Validate clarification questions format
            questions = extracted_data["clarification_questions"]
            validated_questions = []
            
            for question in questions:
                if isinstance(question, dict) and "question" in question:
                    # Ensure required fields
                    if "category" not in question:
                        question["category"] = "business"
                    if "priority" not in question:
                        question["priority"] = "medium"
                    if "rationale" not in question:
                        question["rationale"] = "Clarification needed"
                    
                    validated_questions.append(question)
                elif isinstance(question, str):
                    # Convert string questions to proper format
                    validated_questions.append({
                        "question": question,
                        "category": "business",
                        "priority": "medium",
                        "rationale": "Clarification needed"
                    })
            
            extracted_data["clarification_questions"] = validated_questions
            
            # Enhance confidence score based on content analysis
            enhanced_confidence = self._calculate_enhanced_confidence(
                extracted_data, original_content
            )
            extracted_data["confidence_score"] = enhanced_confidence
            
            return extracted_data
            
        except Exception as e:
            logger.warning(f"Error validating extraction data: {str(e)}")
            return extracted_data

    def _calculate_enhanced_confidence(
        self,
        extracted_data: Dict[str, Any],
        original_content: str
    ) -> float:
        """
        Calculate enhanced confidence score based on content analysis.
        
        Args:
            extracted_data: Extracted requirements data
            original_content: Original document content
            
        Returns:
            Enhanced confidence score (0.0-1.0)
        """
        try:
            base_confidence = extracted_data.get("confidence_score", 0.5)
            
            # Factors that increase confidence
            confidence_boosters = 0.0
            
            # Check for specific requirement keywords
            requirement_keywords = [
                "shall", "must", "should", "will", "requirement", "specification",
                "functional", "non-functional", "performance", "security"
            ]
            
            content_lower = original_content.lower()
            keyword_count = sum(1 for keyword in requirement_keywords if keyword in content_lower)
            confidence_boosters += min(0.2, keyword_count * 0.02)
            
            # Check for structured content
            if any(marker in content_lower for marker in ["1.", "2.", "a.", "b.", "-", "*"]):
                confidence_boosters += 0.1
            
            # Check for stakeholder mentions
            stakeholder_keywords = ["user", "customer", "admin", "manager", "stakeholder"]
            stakeholder_count = sum(1 for keyword in stakeholder_keywords if keyword in content_lower)
            confidence_boosters += min(0.1, stakeholder_count * 0.01)
            
            # Check extracted data quality
            req = extracted_data.get("structured_requirements", {})
            if req.get("functional_requirements") and len(req["functional_requirements"]) > 0:
                confidence_boosters += 0.1
            
            if req.get("business_goals") and len(req["business_goals"]) > 0:
                confidence_boosters += 0.1
            
            # Factors that decrease confidence
            confidence_penalties = 0.0
            
            # Check for ambiguous language
            ambiguous_keywords = ["maybe", "perhaps", "might", "could", "possibly", "unclear"]
            ambiguous_count = sum(1 for keyword in ambiguous_keywords if keyword in content_lower)
            confidence_penalties += min(0.2, ambiguous_count * 0.05)
            
            # Check document length (very short documents are less reliable)
            if len(original_content.strip()) < 100:
                confidence_penalties += 0.3
            
            # Calculate final confidence
            final_confidence = base_confidence + confidence_boosters - confidence_penalties
            return max(0.0, min(1.0, final_confidence))
            
        except Exception as e:
            logger.warning(f"Error calculating enhanced confidence: {str(e)}")
            return extracted_data.get("confidence_score", 0.5)

    def _generate_processing_notes(
        self,
        content: str,
        extracted_data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate processing notes for the extraction.
        
        Args:
            content: Original document content
            extracted_data: Extracted requirements data
            
        Returns:
            List of processing notes
        """
        notes = []
        
        try:
            # Document size note
            if len(content) > 5000:
                notes.append("Large document processed - may have been truncated")
            elif len(content) < 200:
                notes.append("Short document - limited information available")
            
            # Requirements count notes
            req = extracted_data.get("structured_requirements", {})
            func_reqs = req.get("functional_requirements", [])
            if len(func_reqs) > 10:
                notes.append("High number of functional requirements identified")
            elif len(func_reqs) < 3:
                notes.append("Few functional requirements identified - may need more detail")
            
            # Questions and gaps notes
            questions = extracted_data.get("clarification_questions", [])
            gaps = extracted_data.get("identified_gaps", [])
            
            if len(questions) > 8:
                notes.append("Many clarification questions generated - document may be ambiguous")
            
            if len(gaps) > 5:
                notes.append("Multiple gaps identified - requirements may be incomplete")
            
            # Confidence note
            confidence = extracted_data.get("confidence_score", 0.5)
            if confidence < 0.6:
                notes.append("Low confidence score - document may need additional clarification")
            elif confidence > 0.9:
                notes.append("High confidence score - document appears well-structured")
            
        except Exception as e:
            logger.warning(f"Error generating processing notes: {str(e)}")
            notes.append("Error generating processing notes")
        
        return notes

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported file extensions
        """
        return list(self.supported_extensions)

    def get_agent_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities and metadata.
        
        Returns:
            Dictionary with agent capabilities
        """
        return {
            "agent_type": self.agent_type,
            "agent_version": self.agent_version,
            "capabilities": [
                "Text document parsing",
                "Requirements extraction",
                "Structured data generation",
                "Gap identification",
                "Clarification question generation",
                "Confidence scoring"
            ],
            "supported_formats": self.get_supported_formats(),
            "planned_formats": [".pdf", ".pptx", ".docx"],
            "max_document_size": "8000 characters (configurable)",
            "output_format": "Structured JSON with requirements, questions, and gaps"
        }
