"""
Code Generator Component for Vibe Coding Tool

This module implements the Code Generator component that takes parsed intent
and unified context to generate high-quality code using templates and validation.
"""

import os
import time
import ast
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

from app.vibe_coding.models import (
    ParsedIntent, 
    UnifiedContext, 
    CodeGenerationRequest, 
    CodeGenerationResponse
)
from app.core.exceptions import CodeGenerationError, ValidationError, TemplateError


@dataclass
class CodeGeneratorConfig:
    """Configuration for Code Generator"""
    
    max_code_length: int = 5000
    enable_validation: bool = True
    enable_syntax_check: bool = True
    enable_best_practices: bool = True
    template_directory: str = "templates/"
    output_directory: str = "generated/"
    supported_languages: List[str] = field(default_factory=lambda: ["python", "typescript", "javascript"])
    supported_frameworks: List[str] = field(default_factory=lambda: ["fastapi", "react", "express"])


class CodeGenerator:
    """
    Code Generator for Vibe Coding Tool
    
    Generates high-quality code based on parsed intent and unified context
    using templates, validation, and best practices enforcement.
    """
    
    def __init__(self, config: Optional[CodeGeneratorConfig] = None):
        """
        Initialize Code Generator
        
        Args:
            config: Configuration for the code generator
        """
        self.config = config or CodeGeneratorConfig()
        self.templates: Dict[str, str] = {}
        self.validation_rules: Dict[str, List[str]] = {}
        self.best_practices: Dict[str, List[str]] = {}
        self.generation_history: List[Dict[str, Any]] = []
        
        # Initialize validation rules and best practices
        self._initialize_validation_rules()
        self._initialize_best_practices()
    
    def _initialize_validation_rules(self):
        """Initialize validation rules for different languages"""
        self.validation_rules = {
            "python": [
                "Must have proper imports",
                "Must have function definitions",
                "Must have proper indentation",
                "Must have docstrings for functions"
            ],
            "typescript": [
                "Must have proper type annotations",
                "Must have interface definitions",
                "Must have proper imports",
                "Must have proper syntax"
            ],
            "javascript": [
                "Must have proper syntax",
                "Must have proper imports",
                "Must have function definitions",
                "Must have proper formatting"
            ]
        }
    
    def _initialize_best_practices(self):
        """Initialize best practices for different languages and frameworks"""
        self.best_practices = {
            "python": [
                "Use type hints",
                "Use docstrings",
                "Follow PEP 8",
                "Use meaningful variable names",
                "Handle exceptions properly"
            ],
            "fastapi": [
                "Use Pydantic models",
                "Use dependency injection",
                "Use proper HTTP status codes",
                "Use async/await",
                "Use proper error handling"
            ],
            "typescript": [
                "Use strict typing",
                "Use interfaces",
                "Use proper imports",
                "Use meaningful names",
                "Use proper formatting"
            ],
            "react": [
                "Use functional components",
                "Use hooks",
                "Use proper props typing",
                "Use proper state management",
                "Use proper error boundaries"
            ]
        }
    
    async def generate_code(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """
        Generate code based on parsed intent and unified context
        
        Args:
            request: Code generation request with intent and context
            
        Returns:
            CodeGenerationResponse: Generated code with metadata
            
        Raises:
            ValidationError: If request validation fails
            TemplateError: If template loading fails
            CodeGenerationError: If code generation fails
        """
        if not request:
            raise ValidationError("Request cannot be None")
        
        if not request.intent:
            raise ValidationError("Intent is required")
        
        if not request.context:
            raise ValidationError("Context is required")
        
        start_time = time.time()
        
        try:
            # Load template
            template_start = time.time()
            template = self._load_template(
                request.language, 
                request.framework, 
                request.intent.intent_type,
                request.custom_template
            )
            template_loading_time = time.time() - template_start
            
            # Generate code using template
            generated_code = self._render_template(template, request.intent, request.context)
            
            # Validate generated code
            validation_start = time.time()
            validation_passed = self._validate_generated_code(
                generated_code, 
                request.language, 
                request.framework
            )
            validation_time = time.time() - validation_start
            
            if not validation_passed and self.config.enable_validation:
                raise ValidationError("Generated code failed validation")
            
            # Check syntax
            syntax_start = time.time()
            syntax_check_passed = self._check_syntax(generated_code, request.language)
            syntax_check_time = time.time() - syntax_start
            
            if not syntax_check_passed and self.config.enable_syntax_check:
                raise CodeGenerationError("Generated code has syntax errors")
            
            # Check best practices
            practices_start = time.time()
            best_practices_passed = self._check_best_practices(
                generated_code, 
                request.language, 
                request.framework
            )
            best_practices_time = time.time() - practices_start
            
            if not best_practices_passed and self.config.enable_best_practices:
                raise CodeGenerationError("Generated code does not follow best practices")
            
            # Calculate context integration score
            context_integration_score = self._calculate_context_integration_score(
                generated_code, 
                request.context
            )
            
            generation_time = time.time() - start_time
            
            # Create response
            response = CodeGenerationResponse(
                success=True,
                generated_code=generated_code,
                language=request.language,
                framework=request.framework,
                validation_passed=validation_passed,
                syntax_check_passed=syntax_check_passed,
                best_practices_passed=best_practices_passed,
                generation_time=generation_time,
                template_used=f"{request.language}_{request.framework}_{request.intent.intent_type}",
                context_integration_score=context_integration_score,
                template_loading_time=template_loading_time,
                validation_time=validation_time,
                syntax_check_time=syntax_check_time,
                best_practices_time=best_practices_time
            )
            
            # Record in history
            self.generation_history.append({
                "timestamp": datetime.utcnow(),
                "success": True,
                "language": request.language,
                "framework": request.framework,
                "generation_time": generation_time,
                "intent_type": request.intent.intent_type
            })
            
            return response
            
        except Exception as e:
            generation_time = time.time() - start_time
            
            # Record failure in history
            self.generation_history.append({
                "timestamp": datetime.utcnow(),
                "success": False,
                "language": request.language if request else "unknown",
                "framework": request.framework if request else "unknown",
                "generation_time": generation_time,
                "error": str(e)
            })
            
            # Re-raise the exception
            raise
    
    def _load_template(
        self, 
        language: str, 
        framework: str, 
        intent_type: str,
        custom_template: Optional[str] = None
    ) -> str:
        """
        Load template for code generation
        
        Args:
            language: Programming language
            framework: Framework
            intent_type: Type of intent
            custom_template: Custom template to use
            
        Returns:
            str: Template content
            
        Raises:
            TemplateError: If template cannot be loaded
        """
        if custom_template:
            return custom_template
        
        # Check if template is already loaded
        template_key = f"{language}_{framework}_{intent_type}"
        if template_key in self.templates:
            return self.templates[template_key]
        
        # Try to load template from file
        template_path = os.path.join(
            self.config.template_directory,
            language,
            framework,
            f"{intent_type}.template"
        )
        
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                    self.templates[template_key] = template_content
                    return template_content
            except Exception as e:
                raise TemplateError(f"Failed to load template: {e}")
        else:
            # Generate a basic template
            basic_template = self._generate_basic_template(language, framework, intent_type)
            self.templates[template_key] = basic_template
            return basic_template
    
    def _generate_basic_template(self, language: str, framework: str, intent_type: str) -> str:
        """Generate a basic template for the given parameters"""
        if language == "python" and framework == "fastapi":
            return """
# Generated {{ intent.intent_type }} for {{ intent.entities.resource }}
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class {{ intent.entities.resource|title }}Model(BaseModel):
    # Add fields based on context
    pass

@router.post("/{{ intent.entities.resource }}")
async def create_{{ intent.entities.resource }}(data: {{ intent.entities.resource|title }}Model):
    \"\"\"Create a new {{ intent.entities.resource }}.\"\"\"
    # Implementation based on context
    return data

@router.get("/{{ intent.entities.resource }}")
async def get_{{ intent.entities.resource }}s():
    \"\"\"Get all {{ intent.entities.resource }}s.\"\"\"
    # Implementation based on context
    return []
"""
        elif language == "typescript" and framework == "react":
            return """
// Generated {{ intent.intent_type }} component
import React from 'react';

interface {{ intent.entities.resource|title }}Props {
  // Add props based on context
}

const {{ intent.entities.resource|title }}: React.FC<{{ intent.entities.resource|title }}Props> = (props) => {
  // Implementation based on context
  return (
    <div>
      <h1>{{ intent.entities.resource|title }}</h1>
      {/* Add content based on context */}
    </div>
  );
};

export default {{ intent.entities.resource|title }};
"""
        else:
            return f"// Generated {intent_type} for {language} with {framework}\n// Implementation based on context"
    
    def _render_template(
        self, 
        template: str, 
        intent: ParsedIntent, 
        context: UnifiedContext
    ) -> str:
        """
        Render template with intent and context data
        
        Args:
            template: Template string
            intent: Parsed intent
            context: Unified context
            
        Returns:
            str: Rendered code
        """
        # Simple template rendering (in production, use Jinja2 or similar)
        rendered = template
        
        # Replace intent variables
        rendered = rendered.replace("{{ intent.intent_type }}", intent.intent_type)
        rendered = rendered.replace("{{ intent.entities.resource }}", intent.entities.get("resource", "item"))
        rendered = rendered.replace("{{ intent.entities.resource|title }}", intent.entities.get("resource", "item").title())
        
        # Replace context variables
        if context.project_structure:
            backend_models = context.project_structure.get("backend", {}).get("app", {}).get("models", [])
            if backend_models:
                rendered = rendered.replace("{{ context.project_structure.backend.app.models }}", ", ".join(backend_models))
        
        return rendered
    
    def _validate_generated_code(self, code: str, language: str, framework: str) -> bool:
        """
        Validate generated code
        
        Args:
            code: Generated code
            language: Programming language
            framework: Framework
            
        Returns:
            bool: True if validation passes
        """
        if not code or not code.strip():
            return False
        
        # Basic validation rules
        rules = self.validation_rules.get(language, [])
        
        for rule in rules:
            if not self._check_validation_rule(code, rule, language):
                return False
        
        return True
    
    def _check_validation_rule(self, code: str, rule: str, language: str) -> bool:
        """Check a specific validation rule"""
        if rule == "Must have proper imports":
            if language == "python":
                return "import" in code or "from" in code
            elif language in ["typescript", "javascript"]:
                return "import" in code or "require" in code
        
        elif rule == "Must have function definitions":
            if language == "python":
                return "def " in code
            elif language in ["typescript", "javascript"]:
                return "function" in code or "=>" in code or "const" in code
        
        elif rule == "Must have proper indentation":
            # Basic indentation check
            lines = code.split('\n')
            for line in lines:
                if line.strip() and not line.startswith((' ', '\t')):
                    if any(keyword in line for keyword in ['def ', 'class ', 'if ', 'for ', 'while ']):
                        return False
        
        elif rule == "Must have docstrings for functions":
            if language == "python":
                return '"""' in code or "'''" in code
        
        return True
    
    def _check_syntax(self, code: str, language: str) -> bool:
        """
        Check syntax of generated code
        
        Args:
            code: Generated code
            language: Programming language
            
        Returns:
            bool: True if syntax is valid
        """
        if language == "python":
            try:
                ast.parse(code)
                return True
            except SyntaxError:
                return False
        elif language in ["typescript", "javascript"]:
            # Basic syntax check for JS/TS
            try:
                # Check for balanced braces and parentheses
                brace_count = code.count('{') - code.count('}')
                paren_count = code.count('(') - code.count(')')
                bracket_count = code.count('[') - code.count(']')
                
                return brace_count == 0 and paren_count == 0 and bracket_count == 0
            except:
                return False
        
        return True
    
    def _check_best_practices(self, code: str, language: str, framework: str) -> bool:
        """
        Check if code follows best practices
        
        Args:
            code: Generated code
            language: Programming language
            framework: Framework
            
        Returns:
            bool: True if best practices are followed
        """
        practices = self.best_practices.get(language, [])
        framework_practices = self.best_practices.get(framework, [])
        all_practices = practices + framework_practices
        
        for practice in all_practices:
            if not self._check_best_practice(code, practice, language, framework):
                return False
        
        return True
    
    def _check_best_practice(self, code: str, practice: str, language: str, framework: str) -> bool:
        """Check a specific best practice"""
        if practice == "Use type hints" and language == "python":
            return ":" in code and "->" in code
        
        elif practice == "Use docstrings" and language == "python":
            return '"""' in code or "'''" in code
        
        elif practice == "Use Pydantic models" and framework == "fastapi":
            return "BaseModel" in code or "Pydantic" in code
        
        elif practice == "Use async/await" and framework == "fastapi":
            return "async def" in code and "await" in code
        
        elif practice == "Use strict typing" and language == "typescript":
            return ":" in code and "interface" in code
        
        elif practice == "Use functional components" and framework == "react":
            return "React.FC" in code or "function" in code
        
        return True
    
    def _calculate_context_integration_score(self, code: str, context: UnifiedContext) -> float:
        """
        Calculate how well the generated code integrates with the context
        
        Args:
            code: Generated code
            context: Unified context
            
        Returns:
            float: Integration score between 0 and 1
        """
        score = 0.0
        total_checks = 0
        
        # Check if code references existing models
        if context.existing_code:
            for model_name, model_code in context.existing_code.items():
                total_checks += 1
                if model_name.lower() in code.lower():
                    score += 1.0
        
        # Check if code references project structure
        if context.project_structure:
            total_checks += 1
            if any(path in code for path in ["app/", "models/", "api/", "services/"]):
                score += 1.0
        
        # Check if code references dependencies
        if context.dependencies:
            total_checks += 1
            for dep_list in context.dependencies.values():
                for dep in dep_list:
                    if dep.lower() in code.lower():
                        score += 1.0
                        break
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """
        Get generation statistics
        
        Returns:
            Dict[str, Any]: Generation statistics
        """
        if not self.generation_history:
            return {
                "total_generations": 0,
                "successful_generations": 0,
                "failed_generations": 0,
                "success_rate": 0.0,
                "average_generation_time": 0.0,
                "language_distribution": {},
                "framework_distribution": {}
            }
        
        total = len(self.generation_history)
        successful = sum(1 for entry in self.generation_history if entry.get("success", False))
        failed = total - successful
        success_rate = successful / total if total > 0 else 0.0
        
        # Calculate average generation time
        times = [entry.get("generation_time", 0) for entry in self.generation_history if entry.get("generation_time")]
        avg_time = sum(times) / len(times) if times else 0.0
        
        # Language distribution
        language_dist = {}
        for entry in self.generation_history:
            lang = entry.get("language", "unknown")
            language_dist[lang] = language_dist.get(lang, 0) + 1
        
        return {
            "total_generations": total,
            "successful_generations": successful,
            "failed_generations": failed,
            "success_rate": success_rate,
            "average_generation_time": avg_time,
            "language_distribution": language_dist
        }
    
    def clear_generation_history(self):
        """Clear generation history"""
        self.generation_history = []

