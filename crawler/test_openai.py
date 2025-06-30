#!/usr/bin/env python3
"""
Test script to verify OpenAI API v1.0.0 is working
"""
import openai
import os
import json

def test_openai_api():
    """Test the OpenAI API with the new v1.0.0 format"""
    print("=== Testing OpenAI API v1.0.0 ===")
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    print(f"✅ API key found (length: {len(api_key)})")
    
    try:
        # Initialize client
        client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
        
        # Test a simple completion
        test_prompt = "Say 'Hello, OpenAI API v1.0.0 is working!' in one sentence."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use cheaper model for testing
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ API test successful: {result}")
        
        # Test the RFP analysis prompt
        print("\n=== Testing RFP Analysis Prompt ===")
        rfp_prompt = """
You are an AI agent helping an insurance brokerage locate RFPs related only to:
- Employee benefits
- Group health, dental, vision, life, or disability insurance
- Benefits administration
- Insurance procurement

Given this page content from https://example.com:
This is a test page about school district operations and general information.

Return JSON:
{
  "is_rfp": true or false,
  "summary": "Brief summary of the RFP or page content",
  "category": "Employee Benefits" or "Other",
  "submission_deadline": "Deadline date if found, otherwise empty string",
  "submission_location": "Where to submit if found, otherwise empty string",
  "contact_email": "Contact email if found, otherwise empty string",
  "budget_range": "Budget information if found, otherwise empty string",
  "confidence": "High/Medium/Low based on how certain you are this is an insurance RFP"
}
"""
        
        rfp_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": rfp_prompt}],
            temperature=0.1
        )
        
        rfp_result = rfp_response.choices[0].message.content
        print(f"✅ RFP analysis test successful: {rfp_result}")
        
        # Try to parse the JSON response
        try:
            parsed = json.loads(rfp_result)
            print(f"✅ JSON parsing successful: {parsed}")
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}")
            print(f"Raw response: {rfp_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

if __name__ == "__main__":
    test_openai_api() 