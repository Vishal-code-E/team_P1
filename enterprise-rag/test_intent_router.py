"""
Test script for Intent Router Agent
Run this to verify routing decisions before full integration
"""
from agent.intent_router import route_intent
from dotenv import load_dotenv

load_dotenv()

# Test cases
test_queries = [
    ("What is our AWS spending limit?", "RETRIEVE_AND_ANSWER"),
    ("When was the AWS policy last updated?", "RETRIEVE_AND_ANSWER"),
    ("Who approved the AWS budget?", "REFUSE"),
    ("Hello", "ANSWER_DIRECTLY"),
    ("What will our AWS spend be next year?", "REFUSE"),
    ("How are you?", "ANSWER_DIRECTLY"),
    ("What is the current DevOps deployment policy?", "RETRIEVE_AND_ANSWER"),
]

print("=" * 70)
print("Intent Router Test Suite")
print("=" * 70 + "\n")

for query, expected_decision in test_queries:
    result = route_intent(query)
    decision = result.get("decision")
    reason = result.get("reason", "")
    
    status = "✅" if decision == expected_decision else "❌"
    
    print(f"Query: {query}")
    print(f"Expected: {expected_decision}")
    print(f"Got: {decision} {status}")
    print(f"Reason: {reason}")
    print("-" * 70 + "\n")
