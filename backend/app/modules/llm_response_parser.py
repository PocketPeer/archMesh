"""
LLM Response Parser - Provider-specific response handling
"""
import re
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class LLMResponseParser:
    """Parse responses from different LLM providers"""
    
    @staticmethod
    def parse_openai(response_data: Dict[str, Any]) -> str:
        """Parse OpenAI API response"""
        return response_data["choices"][0]["message"]["content"]
    
    @staticmethod
    def parse_anthropic(response_data: Dict[str, Any]) -> str:
        """Parse Anthropic Claude API response"""
        return response_data["content"][0]["text"]
    
    @staticmethod
    def parse_ollama(response_data: Dict[str, Any]) -> str:
        """
        Parse Ollama API response (DeepSeek, Llama, etc.)
        Handles special tokens and reasoning blocks
        """
        # Handle both old and new Ollama API formats
        if "message" in response_data:
            # New chat API format
            response_text = response_data["message"].get("content", "")
        else:
            # Old generate API format
            response_text = response_data.get("response", "")
        
        # Handle DeepSeek R1's special reasoning format
        # DeepSeek R1 uses <think>...</think> for reasoning
        if "<think>" in response_text:
            # Remove thinking blocks - they're not part of the final answer
            response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
        
        # Some models might have wrapped the reasoning differently
        if "<reasoning>" in response_text:
            response_text = re.sub(r'<reasoning>.*?</reasoning>', '', response_text, flags=re.DOTALL)
        
        # Clean up any remaining special tokens
        response_text = response_text.strip()
        
        return response_text
    
    @staticmethod
    def extract_json(text: str) -> str:
        """
        Extract JSON from LLM response text.
        Handles various formats: plain JSON, markdown code blocks, reasoning blocks
        """
        if not text:
            return "{}"
        
        # Remove markdown code blocks - handle both ```json and ``` formats
        # First, remove the opening ```json or ``` at the start
        if text.strip().startswith('```json'):
            text = text.replace('```json', '', 1)
        elif text.strip().startswith('```'):
            text = text.replace('```', '', 1)
        
        # Remove any remaining backticks
        text = re.sub(r'```', '', text)
        
        # Remove thinking/reasoning blocks
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        text = re.sub(r'<reasoning>.*?</reasoning>', '', text, flags=re.DOTALL)
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # Find the main JSON object boundaries
        json_start = text.find('{')
        json_end = text.rfind('}')
        
        if json_start != -1 and json_end != -1 and json_end > json_start:
            # Extract the JSON object
            json_text = text[json_start:json_end + 1]
            
            # Clean up any remaining non-JSON text
            json_text = json_text.strip()
            
            # Fix common JSON issues in PlantUML code
            # Replace unescaped newlines in string values with escaped newlines
            json_text = re.sub(r'"([^"]*)\n([^"]*)"', r'"\1\\n\2"', json_text)
            
            # Replace other control characters that might break JSON
            json_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_text)
            
            return json_text
        else:
            # If no JSON object found, try to find any JSON-like structure
            array_start = text.find('[')
            array_end = text.rfind(']')
            if array_start != -1 and array_end != -1 and array_end > array_start:
                return text[array_start:array_end + 1]
        
        return "{}"
    
    @staticmethod
    def parse_json_response(text: str, fallback: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parse JSON from LLM response with robust error handling
        """
        try:
            # Extract and clean JSON
            cleaned_text = LLMResponseParser.extract_json(text)
            
            # Try to parse
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Response text: {text[:500]}...")
            
            # Try to fix common JSON issues
            try:
                fixed_json = LLMResponseParser._fix_common_json_issues(cleaned_text)
                return json.loads(fixed_json)
            except json.JSONDecodeError as e2:
                logger.error(f"Failed to parse even after fixing JSON issues: {e2}")
                
                if fallback:
                    return fallback
                
                # Return minimal valid structure
                return {"error": "Failed to parse LLM response", "raw_response": text[:200]}
    
    @staticmethod
    def _fix_common_json_issues(json_text: str) -> str:
        """
        Fix common JSON syntax issues that LLMs often produce
        """
        # Fix missing commas between array elements
        json_text = re.sub(r'}\s*\n\s*{', '},\n{', json_text)
        json_text = re.sub(r']\s*\n\s*{', '],\n{', json_text)
        json_text = re.sub(r'}\s*\n\s*\[', '},\n[', json_text)
        
        # Fix missing commas between object properties
        json_text = re.sub(r'"\s*\n\s*"', '",\n"', json_text)
        json_text = re.sub(r'}\s*\n\s*"', '},\n"', json_text)
        json_text = re.sub(r']\s*\n\s*"', '],\n"', json_text)
        
        # Fix trailing commas (remove them)
        json_text = re.sub(r',\s*}', '}', json_text)
        json_text = re.sub(r',\s*]', ']', json_text)
        
        # Fix missing quotes around keys
        json_text = re.sub(r'(\w+):', r'"\1":', json_text)
        
        return json_text

