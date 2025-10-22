"""
Quality Checker - Simple component for checking code quality
"""

import re
from typing import List, Dict, Any
from .models import GeneratedCode, QualityReport, QualityLevel


class QualityChecker:
    """
    Simple quality checker that validates generated code.
    
    Single responsibility: Check code quality and provide feedback
    """
    
    def __init__(self):
        # Simple quality patterns
        self.quality_patterns = {
            "good_practices": [
                r"def\s+\w+\s*\(",  # Function definitions
                r"class\s+\w+\s*:",  # Class definitions
                r"try:",  # Exception handling
                r"except\s+",  # Exception handling
                r"# TODO:",  # TODO comments
                r"\"\"\"",  # Docstrings
                r"async\s+def",  # Async functions
                r"@\w+",  # Decorators
            ],
            "bad_practices": [
                r"print\s*\(",  # Print statements (in production code)
                r"eval\s*\(",  # Eval usage
                r"exec\s*\(",  # Exec usage
                r"import\s+\*",  # Wildcard imports
                r"pass\s*$",  # Pass statements
                r"TODO.*pass",  # TODO with pass
            ],
            "security_issues": [
                r"subprocess\.call",  # Unsafe subprocess calls
                r"os\.system",  # Unsafe system calls
                r"eval\s*\(",  # Eval usage
                r"exec\s*\(",  # Exec usage
                r"pickle\.loads",  # Unsafe pickle usage
            ]
        }
        
        # Language-specific quality rules
        self.language_rules = {
            "python": {
                "indentation": 4,
                "max_line_length": 88,
                "required_imports": ["typing", "pydantic"],
                "style_guide": "PEP 8"
            },
            "javascript": {
                "indentation": 2,
                "max_line_length": 100,
                "required_imports": [],
                "style_guide": "ESLint"
            },
            "typescript": {
                "indentation": 2,
                "max_line_length": 100,
                "required_imports": ["types"],
                "style_guide": "TSLint"
            }
        }
    
    def check(self, generated_code: GeneratedCode) -> QualityReport:
        """
        Check code quality and generate report.
        
        Args:
            generated_code: Code to check
            
        Returns:
            QualityReport: Quality assessment with feedback
        """
        code = generated_code.code
        language = generated_code.language.value
        
        # Calculate quality score
        score = self._calculate_quality_score(code, language)
        
        # Identify issues
        issues = self._identify_issues(code, language)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(code, language, issues)
        
        # Calculate metrics
        metrics = self._calculate_metrics(code, language)
        
        # Determine overall quality level
        quality_level = self._determine_quality_level(score)
        
        return QualityReport(
            overall_quality=quality_level,
            score=score,
            issues=issues,
            suggestions=suggestions,
            metrics=metrics
        )
    
    def _calculate_quality_score(self, code: str, language: str) -> float:
        """Calculate overall quality score"""
        score = 0.5  # Base score
        
        # Good practices bonus
        good_practices = self._count_patterns(code, self.quality_patterns["good_practices"])
        if good_practices > 0:
            score += min(good_practices * 0.1, 0.3)
        
        # Bad practices penalty
        bad_practices = self._count_patterns(code, self.quality_patterns["bad_practices"])
        if bad_practices > 0:
            score -= min(bad_practices * 0.1, 0.3)
        
        # Security issues penalty
        security_issues = self._count_patterns(code, self.quality_patterns["security_issues"])
        if security_issues > 0:
            score -= min(security_issues * 0.2, 0.4)
        
        # Code structure bonus
        if self._has_proper_structure(code, language):
            score += 0.2
        
        # Documentation bonus
        if self._has_documentation(code):
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _count_patterns(self, code: str, patterns: List[str]) -> int:
        """Count occurrences of patterns in code"""
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, code, re.MULTILINE)
            count += len(matches)
        return count
    
    def _has_proper_structure(self, code: str, language: str) -> bool:
        """Check if code has proper structure"""
        if language == "python":
            return "def " in code or "class " in code
        elif language in ["javascript", "typescript"]:
            return "function " in code or "class " in code or "=>" in code
        else:
            return len(code.split('\n')) > 5
    
    def _has_documentation(self, code: str) -> bool:
        """Check if code has documentation"""
        doc_patterns = [r'"""', r"'''", r'/\*', r'//', r'#']
        return any(re.search(pattern, code) for pattern in doc_patterns)
    
    def _identify_issues(self, code: str, language: str) -> List[str]:
        """Identify specific issues in code"""
        issues = []
        
        # Check for bad practices
        for pattern in self.quality_patterns["bad_practices"]:
            if re.search(pattern, code):
                issues.append(f"Bad practice detected: {pattern}")
        
        # Check for security issues
        for pattern in self.quality_patterns["security_issues"]:
            if re.search(pattern, code):
                issues.append(f"Security issue detected: {pattern}")
        
        # Check line length
        max_length = self.language_rules.get(language, {}).get("max_line_length", 100)
        long_lines = [i+1 for i, line in enumerate(code.split('\n')) if len(line) > max_length]
        if long_lines:
            issues.append(f"Lines too long: {long_lines}")
        
        # Check for TODO comments
        if "TODO" in code:
            issues.append("Code contains TODO comments - implementation incomplete")
        
        # Check for pass statements
        if "pass" in code and language == "python":
            issues.append("Code contains 'pass' statements - implementation incomplete")
        
        return issues
    
    def _generate_suggestions(self, code: str, language: str, issues: List[str]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Documentation suggestions
        if not self._has_documentation(code):
            suggestions.append("Add documentation and comments to improve code readability")
        
        # Structure suggestions
        if not self._has_proper_structure(code, language):
            suggestions.append("Improve code structure with proper functions and classes")
        
        # Language-specific suggestions
        if language == "python":
            if "import" not in code:
                suggestions.append("Add necessary imports for your code to work")
            if "def " not in code:
                suggestions.append("Consider organizing code into functions")
        
        elif language in ["javascript", "typescript"]:
            if "function" not in code and "=>" not in code:
                suggestions.append("Consider organizing code into functions")
            if language == "typescript" and "interface" not in code:
                suggestions.append("Consider adding TypeScript interfaces for better type safety")
        
        # Error handling suggestions
        if "try" not in code and "catch" not in code:
            suggestions.append("Add error handling with try-catch blocks")
        
        # Security suggestions
        if any("security" in issue.lower() for issue in issues):
            suggestions.append("Review and fix security issues before production use")
        
        return suggestions
    
    def _calculate_metrics(self, code: str, language: str) -> Dict[str, Any]:
        """Calculate code metrics"""
        lines = code.split('\n')
        
        return {
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#') or line.strip().startswith('//')]),
            "function_count": len(re.findall(r'def\s+\w+|function\s+\w+', code)),
            "class_count": len(re.findall(r'class\s+\w+', code)),
            "complexity_score": self._calculate_complexity_score(code),
            "readability_score": self._calculate_readability_score(code)
        }
    
    def _calculate_complexity_score(self, code: str) -> float:
        """Calculate code complexity score"""
        # Simple complexity calculation
        complexity = 0
        
        # Count control structures
        complexity += len(re.findall(r'\bif\b|\bfor\b|\bwhile\b|\btry\b|\bexcept\b', code))
        
        # Count nested structures
        complexity += len(re.findall(r'\bif.*:\s*\n\s*\bif\b', code, re.MULTILINE))
        
        # Count function calls
        complexity += len(re.findall(r'\w+\s*\(', code))
        
        return min(complexity / 10.0, 1.0)  # Normalize to 0-1
    
    def _calculate_readability_score(self, code: str) -> float:
        """Calculate code readability score"""
        score = 0.5  # Base score
        
        # Line length factor
        lines = code.split('\n')
        long_lines = len([line for line in lines if len(line) > 100])
        if long_lines == 0:
            score += 0.2
        
        # Documentation factor
        if self._has_documentation(code):
            score += 0.2
        
        # Structure factor
        if self._has_proper_structure(code, "python"):
            score += 0.1
        
        return min(score, 1.0)
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score"""
        if score >= 0.8:
            return QualityLevel.EXCELLENT
        elif score >= 0.6:
            return QualityLevel.GOOD
        elif score >= 0.4:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
