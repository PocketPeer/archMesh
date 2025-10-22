"""
Code Generator - Simple component for generating code from natural language
"""

import uuid
import re
from typing import Dict, List, Any
from .models import GeneratedCode, ProgrammingLanguage, CodeComplexity


class CodeGenerator:
    """
    Simple code generator that creates code from natural language.
    
    Single responsibility: Generate code from natural language
    """
    
    def __init__(self):
        # Simple code templates
        self.code_templates = {
            "api_endpoint": {
                "python": """
@app.route('/{endpoint}', methods=['{method}'])
def {function_name}():
    try:
        # TODO: Implement {description}
        return jsonify({{"message": "Success", "data": None}}), 200
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500
""",
                "javascript": """
app.{method}('/{endpoint}', (req, res) => {{
    try {{
        // TODO: Implement {description}
        res.json({{ message: 'Success', data: null }});
    }} catch (error) {{
        res.status(500).json({{ error: error.message }});
    }}
}});
""",
                "typescript": """
app.{method}('/{endpoint}', (req: Request, res: Response) => {{
    try {{
        // TODO: Implement {description}
        res.json({{ message: 'Success', data: null }});
    }} catch (error) {{
        res.status(500).json({{ error: error.message }});
    }}
}});
"""
            },
            "database_model": {
                "python": """
class {model_name}(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    {fields}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {{
            'id': self.id,
            {field_dict}
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }}
""",
                "javascript": """
const {model_name}Schema = new mongoose.Schema({{
    {fields}
    createdAt: {{ type: Date, default: Date.now }},
    updatedAt: {{ type: Date, default: Date.now }}
}});

const {model_name} = mongoose.model('{model_name}', {model_name}Schema);
module.exports = {model_name};
""",
                "typescript": """
interface {model_name} {{
    id: number;
    {fields}
    createdAt: Date;
    updatedAt: Date;
}}

class {model_name}Model {{
    // TODO: Implement CRUD operations
}}
"""
            },
            "utility_function": {
                "python": """
def {function_name}({parameters}):
    \"\"\"
    {description}
    
    Args:
        {param_docs}
    
    Returns:
        {return_type}: {return_description}
    \"\"\"
    try:
        # TODO: Implement {description}
        pass
    except Exception as e:
        raise Exception(f"Error in {function_name}: {{str(e)}}")
""",
                "javascript": """
/**
 * {description}
 * @param {{Object}} {parameters} - {description}
 * @returns {{Promise<{return_type}>}} {return_description}
 */
async function {function_name}({parameters}) {{
    try {{
        // TODO: Implement {description}
        return null;
    }} catch (error) {{
        throw new Error(`Error in {function_name}: ${{error.message}}`);
    }}
}}
""",
                "typescript": """
/**
 * {description}
 * @param {parameters} - {description}
 * @returns Promise<{return_type}> {return_description}
 */
async function {function_name}({parameters}): Promise<{return_type}> {{
    try {{
        // TODO: Implement {description}
        return null as {return_type};
    }} catch (error) {{
        throw new Error(`Error in {function_name}: ${{error.message}}`);
    }}
}}
"""
            }
        }
        
        # Language detection patterns
        self.language_patterns = {
            ProgrammingLanguage.PYTHON: ["python", "flask", "django", "fastapi", "pandas", "numpy"],
            ProgrammingLanguage.JAVASCRIPT: ["javascript", "node", "express", "react", "vue", "angular"],
            ProgrammingLanguage.TYPESCRIPT: ["typescript", "ts", "angular", "nestjs"],
            ProgrammingLanguage.JAVA: ["java", "spring", "maven", "gradle"],
            ProgrammingLanguage.CSHARP: ["c#", "csharp", "dotnet", "asp.net"],
            ProgrammingLanguage.GO: ["go", "golang", "gin", "echo"],
            ProgrammingLanguage.RUST: ["rust", "cargo", "actix", "tokio"]
        }
    
    def generate(self, intent: str, context: Dict[str, Any] = None) -> GeneratedCode:
        """
        Generate code from natural language intent.
        
        Args:
            intent: Natural language description of what to build
            context: Additional context (language, framework, etc.)
            
        Returns:
            GeneratedCode: Generated code with metadata
        """
        if context is None:
            context = {}
        
        # Detect programming language
        language = self._detect_language(intent, context)
        
        # Determine code template
        template_type = self._determine_template_type(intent)
        
        # Generate code using template
        code = self._generate_from_template(intent, language, template_type)
        
        # Calculate complexity
        complexity = self._calculate_complexity(code, intent)
        
        # Calculate confidence
        confidence = self._calculate_confidence(intent, code, language)
        
        return GeneratedCode(
            id=str(uuid.uuid4()),
            language=language,
            code=code,
            description=intent,
            complexity=complexity,
            confidence=confidence,
            metadata={
                "template_type": template_type,
                "intent": intent,
                "context": context
            }
        )
    
    def _detect_language(self, intent: str, context: Dict[str, Any]) -> ProgrammingLanguage:
        """Detect programming language from intent and context"""
        text = intent.lower()
        
        # Check context first
        if "language" in context:
            lang = context["language"].lower()
            for prog_lang in ProgrammingLanguage:
                if prog_lang.value in lang:
                    return prog_lang
        
        # Check intent for language keywords
        for prog_lang, keywords in self.language_patterns.items():
            if any(keyword in text for keyword in keywords):
                return prog_lang
        
        # Default to Python
        return ProgrammingLanguage.PYTHON
    
    def _determine_template_type(self, intent: str) -> str:
        """Determine which template to use based on intent"""
        text = intent.lower()
        
        if any(word in text for word in ["api", "endpoint", "route", "controller"]):
            return "api_endpoint"
        elif any(word in text for word in ["model", "schema", "entity", "table"]):
            return "database_model"
        elif any(word in text for word in ["function", "method", "utility", "helper"]):
            return "utility_function"
        else:
            return "utility_function"  # Default
    
    def _generate_from_template(self, intent: str, language: ProgrammingLanguage, template_type: str) -> str:
        """Generate code using the appropriate template"""
        if template_type not in self.code_templates:
            template_type = "utility_function"
        
        if language not in self.code_templates[template_type]:
            # Fallback to Python if language not supported
            language = ProgrammingLanguage.PYTHON
        
        template = self.code_templates[template_type][language.value]
        
        # Simple template variable replacement
        code = template.format(
            endpoint=self._extract_endpoint(intent),
            method=self._extract_method(intent),
            function_name=self._extract_function_name(intent),
            description=intent,
            model_name=self._extract_model_name(intent),
            fields=self._extract_fields(intent),
            field_dict=self._extract_field_dict(intent),
            parameters=self._extract_parameters(intent),
            param_docs=self._extract_param_docs(intent),
            return_type=self._extract_return_type(intent),
            return_description=self._extract_return_description(intent)
        )
        
        return code.strip()
    
    def _extract_endpoint(self, intent: str) -> str:
        """Extract endpoint from intent"""
        # Simple extraction - look for common patterns
        if "/" in intent:
            return "/" + intent.split("/")[-1].split()[0]
        return "/api/endpoint"
    
    def _extract_method(self, intent: str) -> str:
        """Extract HTTP method from intent"""
        text = intent.lower()
        if "get" in text or "fetch" in text or "retrieve" in text:
            return "get"
        elif "post" in text or "create" in text or "add" in text:
            return "post"
        elif "put" in text or "update" in text or "modify" in text:
            return "put"
        elif "delete" in text or "remove" in text:
            return "delete"
        else:
            return "get"
    
    def _extract_function_name(self, intent: str) -> str:
        """Extract function name from intent"""
        # Simple snake_case conversion
        words = re.findall(r'\w+', intent.lower())
        return "_".join(words[:3])  # Take first 3 words
    
    def _extract_model_name(self, intent: str) -> str:
        """Extract model name from intent"""
        words = re.findall(r'\w+', intent)
        if words:
            return words[0].capitalize()
        return "Model"
    
    def _extract_fields(self, intent: str) -> str:
        """Extract fields from intent"""
        # Simple field extraction
        return "name = db.Column(db.String(100), nullable=False)\n    email = db.Column(db.String(100), unique=True, nullable=False)"
    
    def _extract_field_dict(self, intent: str) -> str:
        """Extract field dictionary from intent"""
        return "'name': self.name,\n            'email': self.email,"
    
    def _extract_parameters(self, intent: str) -> str:
        """Extract parameters from intent"""
        return "data"
    
    def _extract_param_docs(self, intent: str) -> str:
        """Extract parameter documentation from intent"""
        return "data: Input data"
    
    def _extract_return_type(self, intent: str) -> str:
        """Extract return type from intent"""
        return "dict"
    
    def _extract_return_description(self, intent: str) -> str:
        """Extract return description from intent"""
        return "Processed result"
    
    def _calculate_complexity(self, code: str, intent: str) -> CodeComplexity:
        """Calculate code complexity"""
        lines = len(code.split('\n'))
        words = len(intent.split())
        
        if lines > 20 or words > 10:
            return CodeComplexity.COMPLEX
        elif lines > 10 or words > 5:
            return CodeComplexity.MEDIUM
        else:
            return CodeComplexity.SIMPLE
    
    def _calculate_confidence(self, intent: str, code: str, language: ProgrammingLanguage) -> float:
        """Calculate confidence in generated code"""
        confidence = 0.5  # Base confidence
        
        # Intent clarity factor
        if len(intent.split()) > 3:
            confidence += 0.2
        
        # Language match factor
        if language.value in intent.lower():
            confidence += 0.2
        
        # Code structure factor
        if "def " in code or "function" in code or "class " in code:
            confidence += 0.1
        
        return min(confidence, 1.0)
