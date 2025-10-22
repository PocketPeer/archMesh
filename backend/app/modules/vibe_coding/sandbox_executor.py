"""
Sandbox Executor - Simple component for executing code safely
"""

import subprocess
import tempfile
import os
import time
import psutil
from typing import Dict, Any
from .models import GeneratedCode, ExecutionResult, ExecutionStatus


class SandboxExecutor:
    """
    Simple sandbox executor that runs code safely.
    
    Single responsibility: Execute code safely in sandbox
    """
    
    def __init__(self):
        self.max_execution_time = 30.0  # 30 seconds max
        self.max_memory_mb = 100  # 100MB max
        self.supported_languages = {
            "python": self._execute_python,
            "javascript": self._execute_javascript,
            "typescript": self._execute_typescript
        }
    
    def execute(self, generated_code: GeneratedCode) -> ExecutionResult:
        """
        Execute generated code safely.
        
        Args:
            generated_code: Code to execute
            
        Returns:
            ExecutionResult: Execution result with output/error
        """
        language = generated_code.language.value
        
        if language not in self.supported_languages:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=f"Language {language} not supported for execution",
                execution_time=0.0,
                memory_usage=0.0
            )
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(language), delete=False) as f:
                f.write(generated_code.code)
                temp_file = f.name
            
            # Execute code
            start_time = time.time()
            result = self.supported_languages[language](temp_file)
            execution_time = time.time() - start_time
            
            # Clean up
            os.unlink(temp_file)
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output=result.get("output", ""),
                error=result.get("error", ""),
                execution_time=execution_time,
                memory_usage=result.get("memory_usage", 0.0),
                metadata={
                    "language": language,
                    "file_size": len(generated_code.code)
                }
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                error="Code execution timed out",
                execution_time=self.max_execution_time,
                memory_usage=0.0
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.RUNTIME_ERROR,
                error=f"Execution failed: {str(e)}",
                execution_time=0.0,
                memory_usage=0.0
            )
    
    def _execute_python(self, file_path: str) -> Dict[str, Any]:
        """Execute Python code"""
        try:
            result = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True,
                timeout=self.max_execution_time,
                cwd=os.path.dirname(file_path)
            )
            
            return {
                "output": result.stdout,
                "error": result.stderr,
                "memory_usage": self._get_memory_usage()
            }
        except subprocess.TimeoutExpired:
            raise subprocess.TimeoutExpired("python", self.max_execution_time)
    
    def _execute_javascript(self, file_path: str) -> Dict[str, Any]:
        """Execute JavaScript code"""
        try:
            result = subprocess.run(
                ["node", file_path],
                capture_output=True,
                text=True,
                timeout=self.max_execution_time,
                cwd=os.path.dirname(file_path)
            )
            
            return {
                "output": result.stdout,
                "error": result.stderr,
                "memory_usage": self._get_memory_usage()
            }
        except subprocess.TimeoutExpired:
            raise subprocess.TimeoutExpired("node", self.max_execution_time)
    
    def _execute_typescript(self, file_path: str) -> Dict[str, Any]:
        """Execute TypeScript code (compile first)"""
        try:
            # Compile TypeScript
            compile_result = subprocess.run(
                ["tsc", file_path, "--outDir", os.path.dirname(file_path)],
                capture_output=True,
                text=True,
                timeout=10.0
            )
            
            if compile_result.returncode != 0:
                return {
                    "output": "",
                    "error": f"TypeScript compilation failed: {compile_result.stderr}",
                    "memory_usage": 0.0
                }
            
            # Execute compiled JavaScript
            js_file = file_path.replace('.ts', '.js')
            result = subprocess.run(
                ["node", js_file],
                capture_output=True,
                text=True,
                timeout=self.max_execution_time,
                cwd=os.path.dirname(file_path)
            )
            
            # Clean up compiled file
            if os.path.exists(js_file):
                os.unlink(js_file)
            
            return {
                "output": result.stdout,
                "error": result.stderr,
                "memory_usage": self._get_memory_usage()
            }
        except subprocess.TimeoutExpired:
            raise subprocess.TimeoutExpired("tsc", self.max_execution_time)
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java",
            "csharp": ".cs",
            "go": ".go",
            "rust": ".rs"
        }
        return extensions.get(language, ".txt")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except:
            return 0.0
    
    def validate_execution_environment(self) -> Dict[str, Any]:
        """Validate that execution environment is ready"""
        validation = {
            "python": self._check_command("python"),
            "node": self._check_command("node"),
            "tsc": self._check_command("tsc"),
            "java": self._check_command("java"),
            "go": self._check_command("go"),
            "rust": self._check_command("rustc")
        }
        
        return validation
    
    def _check_command(self, command: str) -> bool:
        """Check if command is available"""
        try:
            subprocess.run([command, "--version"], capture_output=True, timeout=5.0)
            return True
        except:
            return False
