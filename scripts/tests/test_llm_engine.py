"""
Test the llm_engine.infer_gender() function end-to-end against the live DeepSeek bridge.
Run AFTER starting scripts/deepseek_bridge.py in a separate terminal.
"""
import sys, os
sys.path.append(os.getcwd())

from wikihow.llm_engine import infer_gender, set_config

# Make sure we're pointing at our local bridge
set_config({"primary_provider": "deepseek_custom", "deepseek_custom_url": "http://localhost:8002"})

TEST_CASES = [
    {
        "username": "Whimaway",
        "real_name": "Sarah Eliza",
        "location": "Dubai",
        "genderize_guess": "female",
        "genderize_confidence": 0.98,
        "image_ai_guess": "female",
    },
    {
        "username": "Varun Gera",
        "real_name": "unknown",
        "location": "unknown",
        "genderize_guess": "male",
        "genderize_confidence": 0.90,
        "image_ai_guess": "unknown",
    },
]

def main():
    print("=" * 55)
    print("WikiHow LLM Engine — Integration Test (DeepSeek)")
    print("=" * 55)

    for case in TEST_CASES:
        print(f"\n🔍 Testing: {case['username']}")
        result = infer_gender(**case)
        print(f"  Status       : {result.get('status')}")
        print(f"  Identity Tags: {result.get('identity_tags')}")
        print(f"  Confidence   : {result.get('confidence')}")
        print(f"  Source       : {result.get('source')}")
        print(f"  How Predicted: {result.get('how_predicted')}")
        print("-" * 40)

if __name__ == "__main__":
    main()
