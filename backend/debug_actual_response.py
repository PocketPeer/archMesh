#!/usr/bin/env python3
"""
Test with actual LLM response
"""

import json
import re

def test_actual_response():
    """Test with actual LLM response"""
    
    # Read the actual response file
    with open('debug_raw_llm_response.txt', 'r') as f:
        sample_text = f.read()
    
    print("🧪 Testing Actual LLM Response...")
    print(f"📄 Original text length: {len(sample_text)}")
    print(f"📄 First 100 chars: {repr(sample_text[:100])}")
    
    # Test the current extraction logic
    text = sample_text
    
    # Remove markdown code blocks - handle both ```json and ``` formats
    # First, remove the opening ```json or ``` at the start
    if text.strip().startswith('```json'):
        text = text.replace('```json', '', 1)
    elif text.strip().startswith('```'):
        text = text.replace('```', '', 1)
    
    # Remove any remaining backticks
    text = re.sub(r'```', '', text)
    
    print(f"🔧 After backtick removal: {repr(text[:100])}")
    
    # Find the main JSON object boundaries
    json_start = text.find('{')
    json_end = text.rfind('}')
    
    print(f"🔍 JSON start: {json_start}, JSON end: {json_end}")
    
    if json_start != -1 and json_end != -1 and json_end > json_start:
        # Extract the JSON object
        json_text = text[json_start:json_end + 1]
        
        print(f"📄 Extracted JSON length: {len(json_text)}")
        print(f"📄 Extracted JSON (first 200 chars): {repr(json_text[:200])}")
        
        # Try to parse
        try:
            parsed = json.loads(json_text)
            print("✅ JSON parsing successful!")
            print(f"📊 Parsed keys: {list(parsed.keys())}")
            return parsed
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"📄 Error at position: {e.pos}")
            print(f"📄 Context around error: {json_text[max(0, e.pos-50):e.pos+50]}")
            
            # Try to find the specific issue
            lines = json_text[:e.pos].split('\n')
            last_newline = json_text[:e.pos].rfind('\n')
            column = e.pos - last_newline
            print(f"📄 Error at line {len(lines)}, column {column}")
            print(f"📄 Problematic line: {lines[-1] if lines else 'N/A'}")
            
            return None
    else:
        print("❌ No JSON object found")
        return None

if __name__ == "__main__":
    test_actual_response()
