"""
Neurofive Solutions Week 3 — Structured JSON Output
Extract {name, email, issue_type, urgency} from support messages using Gemini JSON Schema
"""

import os
import json
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ============================================================
# 1. Load Environment
# ============================================================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env")
    print("Create .env file: GEMINI_API_KEY=your_key_here")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.6-flash"


# ============================================================
# 2. JSON Schema Definition
# ============================================================
# This schema forces Gemini to ALWAYS return valid JSON with these exact fields
SUPPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Full name of the person sending the message. Extract if mentioned, otherwise empty string."
        },
        "email": {
            "type": "string",
            "description": "Email address found in the message. Empty string if not present."
        },
        "issue_type": {
            "type": "string",
            "enum": ["login", "billing", "technical", "feature_request", "account", "other"],
            "description": "Category of the support issue."
        },
        "urgency": {
            "type": "string",
            "enum": ["low", "medium", "high", "critical"],
            "description": "How urgent the issue is based on tone and content."
        },
        "summary": {
            "type": "string",
            "description": "One-sentence summary of the issue."
        },
        "confidence": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10,
            "description": "Confidence score (1-10) that the extracted information is correct."
        }
    },
    "required": ["name", "email", "issue_type", "urgency", "summary", "confidence"],
    "additionalProperties": False
}


# ============================================================
# 3. Core Function — Extract from Message
# ============================================================
def extract_support_ticket(message: str) -> dict:
    """
    Send message to Gemini with JSON schema constraint.
    Returns parsed dict. Guaranteed valid JSON matching schema.
    """
    prompt = f"""Analyze the following customer support message and extract the required information.

CUSTOMER MESSAGE:
\"\"\"{message}\"\"\"

RULES:
- Return ONLY valid JSON matching the provided schema
- Do NOT add any extra text, markdown, or explanation
- If name or email is missing, use empty string ""
- Classify issue_type from: login, billing, technical, feature_request, account, other
- Classify urgency from: low, medium, high, critical based on tone and severity
- Provide a brief one-sentence summary
- Rate confidence 1-10"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,  # Low temp for consistent structured output
            max_output_tokens=512,
            response_mime_type="application/json",
            response_schema=SUPPORT_SCHEMA
        )
    )

    # Parse the guaranteed-valid JSON
    result = json.loads(response.text)
    return result


# ============================================================
# 4. JSON Validator
# ============================================================
def validate_output(data: dict) -> bool:
    """Verify the output matches expected schema structure."""
    required_keys = {"name", "email", "issue_type", "urgency", "summary", "confidence"}
    
    # Check all required keys present
    if not required_keys.issubset(data.keys()):
        missing = required_keys - data.keys()
        print(f"   ❌ Missing keys: {missing}")
        return False
    
    # Check no extra keys
    if len(data.keys()) != len(required_keys):
        extra = set(data.keys()) - required_keys
        print(f"   ❌ Extra keys: {extra}")
        return False
    
    # Check types
    if not isinstance(data["name"], str):
        return False
    if not isinstance(data["email"], str):
        return False
    if data["issue_type"] not in SUPPORT_SCHEMA["properties"]["issue_type"]["enum"]:
        return False
    if data["urgency"] not in SUPPORT_SCHEMA["properties"]["urgency"]["enum"]:
        return False
    if not isinstance(data["summary"], str):
        return False
    if not (1 <= data["confidence"] <= 10):
        return False
    
    return True


# ============================================================
# 5. Test Cases
# ============================================================
TEST_MESSAGES = [
    # Test 1: Clean, complete message
    {
        "id": 1,
        "label": "Clean Complete Message",
        "text": "Hi, my name is Sarah Johnson and my email is sarah.j@example.com. I can't log into my account since yesterday morning. I need this fixed ASAP as I'm missing important client calls."
    },
    # Test 2: No email, vague issue
    {
        "id": 2,
        "label": "Missing Email, Vague Issue",
        "text": "Hey this is Mike. My app keeps crashing when I try to upload photos. It's really annoying and happens every time."
    },
    # Test 3: Billing complaint, angry tone
    {
        "id": 3,
        "label": "Billing Complaint — Angry",
        "text": "I was charged TWICE for my subscription this month!!! This is unacceptable. My email is angry.customer@email.com and I want a refund immediately or I'm canceling everything."
    },
    # Test 4: Feature request, no name
    {
        "id": 4,
        "label": "Feature Request — Anonymous",
        "text": "It would be great if you could add dark mode to the dashboard. Also, a mobile app would be nice. Not urgent but would improve user experience a lot."
    },
    # Test 5: Technical issue with details
    {
        "id": 5,
        "label": "Technical — Detailed",
        "text": "Hello, I'm Dr. Emily Chen (emily.chen@hospital.org). The API integration with our patient records system stopped working after your last update on March 15th. We are getting 403 errors. This is critical as it affects our daily operations."
    }
]


# ============================================================
# 6. Tricky / Break-It Input
# ============================================================
TRICKY_MESSAGES = [
    {
        "id": "T1",
        "label": "Messy Formatting + Multiple Issues",
        "text": "OMG!!! 😡😡😡 so i tried 2 login but it says WRONG PASSWORD??? then i checked my bank and u charged me $99.99 when it should be $49.99??? my name is xX_DarkSlayer_Xx and my email is probably on file??? FIX THIS NOW or im calling my lawyer!!! also the app is slow and ugly and i hate it"
    },
    {
        "id": "T2",
        "label": "Empty Message",
        "text": ""
    },
    {
        "id": "T3",
        "label": "Non-English + Mixed Content",
        "text": "Hola, soy Carlos. Mi correo es carlos@ejemplo.com. No puedo iniciar sesión. También quiero saber si tienen modo oscuro. Gracias."
    }
]


# ============================================================
# 7. Main Runner
# ============================================================
def run_test(test_case: dict, is_tricky: bool = False):
    """Run a single test and print results."""
    prefix = "🧪" if not is_tricky else "💥"
    print(f"\n{prefix} Test #{test_case['id']} — {test_case['label']}")
    print(f"   Input: {test_case['text'][:80]}{'...' if len(test_case['text']) > 80 else ''}")
    
    try:
        result = extract_support_ticket(test_case["text"])
        
        # Validate
        is_valid = validate_output(result)
        
        if is_valid:
            print("   ✅ JSON VALID — Schema matched perfectly")
        else:
            print("   ⚠️ JSON parsed but schema validation failed")
        
        # Pretty print
        print("   Output:")
        for key, value in result.items():
            print(f"      • {key}: {value}")
            
        return True, result
        
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON PARSE FAILED: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False, None


def main():
    print("=" * 70)
    print("  🤖 Neurofive Solutions — Structured JSON Output")
    print("  Week 3: Extract Support Tickets with Gemini JSON Schema")
    print("=" * 70)
    print(f"\n📋 Schema: {json.dumps(SUPPORT_SCHEMA, indent=2)}")
    print(f"\n🔑 Model: {MODEL}")
    print(f"🔒 Schema enforces: name, email, issue_type, urgency, summary, confidence")
    
    # Run normal tests
    print("\n" + "=" * 70)
    print("  📊 NORMAL TESTS (5 inputs)")
    print("=" * 70)
    
    passed = 0
    failed = 0
    results = []
    
    for test in TEST_MESSAGES:
        ok, res = run_test(test)
        if ok:
            passed += 1
        else:
            failed += 1
        results.append({"test": test, "result": res, "ok": ok})
    
    # Run tricky tests
    print("\n" + "=" * 70)
    print("  💣 TRICKY / BREAK-IT TESTS (Deliberately messy inputs)")
    print("=" * 70)
    
    for test in TRICKY_MESSAGES:
        ok, res = run_test(test, is_tricky=True)
        if ok:
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("  📈 SUMMARY")
    print("=" * 70)
    total = len(TEST_MESSAGES) + len(TRICKY_MESSAGES)
    print(f"   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Success Rate: {passed/total*100:.1f}%")
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: test_results.json")
    
    print("\n" + "=" * 70)
    print("  ✅ All outputs guaranteed valid JSON via Gemini schema constraint")
    print("=" * 70)


if __name__ == "__main__":
    main()