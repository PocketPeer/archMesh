#!/usr/bin/env python3
"""
Simple JSON extraction test
"""

import json
import re

def test_simple_extraction():
    """Test simple JSON extraction"""
    
    # Sample text with backticks
    sample_text = """```
{
  "architecture_overview": {
    "name": "Cloud-Native E-commerce Platform",
    "style": "microservices",
    "description": "Comprehensive e-commerce platform"
  }
}
```"""
    
    print("🧪 Testing Simple JSON Extraction...")
    print(f"📄 Original text: {repr(sample_text[:50])}")
    
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
    
    print(f"🔧 After backtick removal: {repr(text[:50])}")
    
    # Find the main JSON object boundaries
    json_start = text.find('{')
    json_end = text.rfind('}')
    
    print(f"🔍 JSON start: {json_start}, JSON end: {json_end}")
    
    if json_start != -1 and json_end != -1 and json_end > json_start:
        # Extract the JSON object
        json_text = text[json_start:json_end + 1]
        
        print(f"📄 Extracted JSON: {repr(json_text[:100])}")
        
        # Try to parse
        try:
            parsed = json.loads(json_text)
            print("✅ JSON parsing successful!")
            print(f"📊 Parsed keys: {list(parsed.keys())}")
            return parsed
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"📄 Error at position: {e.pos}")
            print(f"📄 Context around error: {json_text[max(0, e.pos-20):e.pos+20]}")
            return None
    else:
        print("❌ No JSON object found")
        return None

if __name__ == "__main__":
    test_simple_extraction()
