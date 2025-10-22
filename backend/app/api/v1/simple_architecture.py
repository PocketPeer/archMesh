"""
Simple Architecture API - Exposes the modular ArchMesh system
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid

from app.modules.requirements import InputParser, RequirementsExtractor, RequirementsValidator
from app.modules.architecture import ArchitectureGenerator, DiagramRenderer, RecommendationEngine
from app.modules.vibe_coding import CodeGenerator, SandboxExecutor, QualityChecker

router = APIRouter(prefix="/simple-architecture", tags=["Simple Architecture"])

# Request/Response Models
class ArchitectureRequest(BaseModel):
    input_text: str
    domain: Optional[str] = "cloud-native"
    complexity: Optional[str] = "medium"

class ArchitectureResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]

class RequirementsAnalysis(BaseModel):
    business_goals: List[Dict[str, Any]]
    functional_requirements: List[Dict[str, Any]]
    non_functional_requirements: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    stakeholders: List[Dict[str, Any]]
    validation_score: float
    validation_status: str

class ArchitectureDesign(BaseModel):
    name: str
    style: str
    description: str
    components: List[Dict[str, Any]]
    technology_stack: Dict[str, List[str]]
    quality_score: float

class DiagramInfo(BaseModel):
    title: str
    description: str
    type: str
    code: str

class RecommendationInfo(BaseModel):
    id: str
    priority: str
    title: str
    description: str
    impact: str
    effort: str
    cost: str

@router.post("/analyze", response_model=ArchitectureResponse)
async def analyze_requirements(request: ArchitectureRequest):
    """
    Analyze requirements and generate architecture using the simple modular system
    """
    try:
        # Step 1: Parse Input
        parser = InputParser()
        parsed_input = parser.parse(request.input_text)
        
        # Step 2: Extract Requirements
        extractor = RequirementsExtractor()
        extracted_requirements = await extractor.extract(parsed_input)
        
        # Step 3: Validate Requirements
        validator = RequirementsValidator()
        validation_result = validator.validate(extracted_requirements)
        
        # Step 4: Generate Architecture
        generator = ArchitectureGenerator()
        architecture = await generator.generate(extracted_requirements, request.domain)
        
        # Step 5: Render Diagrams
        renderer = DiagramRenderer()
        diagrams = renderer.render(architecture)
        
        # Step 6: Generate Recommendations
        recommender = RecommendationEngine()
        recommendations = recommender.generate(architecture)
        
        # Format response
        requirements_analysis = RequirementsAnalysis(
            business_goals=[req.dict() for req in extracted_requirements.business_goals],
            functional_requirements=[req.dict() for req in extracted_requirements.functional_requirements],
            non_functional_requirements=[req.dict() for req in extracted_requirements.non_functional_requirements],
            constraints=[req.dict() for req in extracted_requirements.constraints],
            stakeholders=[req.dict() for req in extracted_requirements.stakeholders],
            validation_score=validation_result.score,
            validation_status=validation_result.status.value
        )
        
        architecture_design = ArchitectureDesign(
            name=architecture.name,
            style=architecture.style.value,
            description=architecture.description,
            components=[comp.dict() for comp in architecture.components],
            technology_stack=architecture.technology_stack.dict(),
            quality_score=architecture.quality_score
        )
        
        diagram_list = [
            DiagramInfo(
                title=diagram.title,
                description=diagram.description,
                type=diagram.type.value,
                code=diagram.content
            ) for diagram in diagrams
        ]
        
        recommendation_list = [
            RecommendationInfo(
                id=rec.id,
                priority=rec.priority.value,
                title=rec.title,
                description=rec.description,
                impact=rec.impact,
                effort=rec.effort,
                cost=rec.cost
            ) for rec in recommendations
        ]
        
        # Get enhanced LLM analysis if available
        llm_analysis = architecture.metadata.get("llm_analysis", {})
        
        return ArchitectureResponse(
            success=True,
            message="Architecture analysis completed successfully",
            data={
                "requirements": requirements_analysis.dict(),
                "architecture": architecture_design.dict(),
                "diagrams": [diagram.dict() for diagram in diagram_list],
                "recommendations": [rec.dict() for rec in recommendation_list],
                # Enhanced LLM analysis data
                "architecture_details": llm_analysis.get("architecture_overview", {}),
                "components_detailed": llm_analysis.get("components", []),
                "diagrams_enhanced": {
                    "c4_context": llm_analysis.get("diagrams", {}).get("c4_context", {}),
                    "c4_container": llm_analysis.get("diagrams", {}).get("c4_container", {}),
                    "sequence_diagrams": llm_analysis.get("diagrams", {}).get("sequence_diagrams", [])
                },
                "implementation_plan": llm_analysis.get("implementation_plan", {}),
                "quality_analysis": llm_analysis.get("quality_analysis", {}),
                "tradeoffs": llm_analysis.get("tradeoffs", []),
                "risks": llm_analysis.get("risks", []),
                "metadata": {
                    "input_confidence": parsed_input.confidence,
                    "total_requirements": len(extracted_requirements.business_goals) + 
                                       len(extracted_requirements.functional_requirements) +
                                       len(extracted_requirements.non_functional_requirements) +
                                       len(extracted_requirements.constraints) +
                                       len(extracted_requirements.stakeholders),
                    "diagram_count": len(diagrams),
                    "recommendation_count": len(recommendations),
                    "llm_enhanced": bool(llm_analysis),
                    "generation_method": architecture.metadata.get("generated_from", "unknown")
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Architecture analysis failed: {str(e)}")

@router.post("/generate-code", response_model=ArchitectureResponse)
async def generate_code(request: ArchitectureRequest):
    """
    Generate code using the Vibe Coding module
    """
    try:
        # Step 1: Generate Code
        code_generator = CodeGenerator()
        generated_code = code_generator.generate(request.input_text)
        
        # Step 2: Check Quality
        quality_checker = QualityChecker()
        quality_report = quality_checker.check_quality(generated_code.code)
        
        # Step 3: Validate Execution Environment
        sandbox_executor = SandboxExecutor()
        env_validation = sandbox_executor.validate_environment()
        
        return ArchitectureResponse(
            success=True,
            message="Code generation completed successfully",
            data={
                "generated_code": generated_code.dict(),
                "quality_report": quality_report.dict(),
                "environment_validation": env_validation.dict(),
                "metadata": {
                    "language": generated_code.language,
                    "complexity": generated_code.complexity,
                    "quality_score": quality_report.overall_score,
                    "execution_ready": env_validation.is_valid
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check for the simple architecture system
    """
    return {
        "status": "healthy",
        "modules": {
            "requirements": "available",
            "architecture": "available", 
            "vibe_coding": "available"
        },
        "message": "Simple modular ArchMesh system is operational"
    }
