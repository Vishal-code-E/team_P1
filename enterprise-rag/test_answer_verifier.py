"""
Test script for Answer Verification Agent
Tests the verifier's ability to detect supported vs unsupported claims
"""
from agent.answer_verifier import verify_answer
from dotenv import load_dotenv

load_dotenv()

# Mock source document class
class MockDocument:
    def __init__(self, content):
        self.page_content = content
        self.metadata = {"source": "test_doc.md"}

# Test cases
print("=" * 80)
print("Answer Verifier Test Suite")
print("=" * 80 + "\n")

# Test 1: Valid answer - fully supported
print("TEST 1: Valid Answer (Fully Supported)")
print("-" * 80)
source_docs = [
    MockDocument("The monthly AWS spending limit for the organization is ₹18,00,000. Alerts are triggered at 80% usage.")
]
question = "What is our AWS spending limit?"
answer = "The monthly AWS spending limit is ₹18,00,000."
result = verify_answer(question, answer, source_docs)
print(f"Question: {question}")
print(f"Answer: {answer}")
print(f"Expected: VALID (True)")
print(f"Got: {'VALID (True)' if result else 'INVALID (False)'} {'✅' if result else '❌'}")
print("\n")

# Test 2: Invalid answer - contains hallucination
print("TEST 2: Invalid Answer (Contains Hallucination)")
print("-" * 80)
source_docs = [
    MockDocument("The monthly AWS spending limit for the organization is ₹18,00,000. Alerts are triggered at 80% usage.")
]
question = "What is our AWS spending limit?"
answer = "The monthly AWS spending limit is ₹18,00,000, approved by the CFO in March 2024."
result = verify_answer(question, answer, source_docs)
print(f"Question: {question}")
print(f"Answer: {answer}")
print(f"Expected: INVALID (False) - 'CFO' and 'March 2024' not in sources")
print(f"Got: {'VALID (True)' if result else 'INVALID (False)'} {'✅' if not result else '❌'}")
print("\n")

# Test 3: Invalid answer - pure speculation
print("TEST 3: Invalid Answer (Pure Speculation)")
print("-" * 80)
source_docs = [
    MockDocument("The monthly AWS spending limit for the organization is ₹18,00,000. Alerts are triggered at 80% usage.")
]
question = "What will our AWS spending be next year?"
answer = "The AWS spending will likely increase to ₹20,00,000 next year."
result = verify_answer(question, answer, source_docs)
print(f"Question: {question}")
print(f"Answer: {answer}")
print(f"Expected: INVALID (False) - speculative claim")
print(f"Got: {'VALID (True)' if result else 'INVALID (False)'} {'✅' if not result else '❌'}")
print("\n")

# Test 4: Invalid - no sources
print("TEST 4: Invalid Answer (No Sources)")
print("-" * 80)
source_docs = []
question = "What is our AWS spending limit?"
answer = "The monthly AWS spending limit is ₹18,00,000."
result = verify_answer(question, answer, source_docs)
print(f"Question: {question}")
print(f"Answer: {answer}")
print(f"Expected: INVALID (False) - no source documents")
print(f"Got: {'VALID (True)' if result else 'INVALID (False)'} {'✅' if not result else '❌'}")
print("\n")

# Test 5: Valid answer with date
print("TEST 5: Valid Answer (Date Information)")
print("-" * 80)
source_docs = [
    MockDocument("This AWS Budget Policy was last updated on August 12, 2024.")
]
question = "When was the AWS policy last updated?"
answer = "The AWS Budget Policy was last updated on August 12, 2024."
result = verify_answer(question, answer, source_docs)
print(f"Question: {question}")
print(f"Answer: {answer}")
print(f"Expected: VALID (True)")
print(f"Got: {'VALID (True)' if result else 'INVALID (False)'} {'✅' if result else '❌'}")
print("\n")

# Test 6: Invalid - answer about something not in docs
print("TEST 6: Invalid Answer (Information Not in Documents)")
print("-" * 80)
source_docs = [
    MockDocument("The monthly AWS spending limit for the organization is ₹18,00,000. Alerts are triggered at 80% usage.")
]
question = "Who approved the AWS budget?"
answer = "The AWS budget was approved by John Smith, the Chief Financial Officer."
result = verify_answer(question, answer, source_docs)
print(f"Question: {question}")
print(f"Answer: {answer}")
print(f"Expected: INVALID (False) - approver name not in sources")
print(f"Got: {'VALID (True)' if result else 'INVALID (False)'} {'✅' if not result else '❌'}")
print("\n")

print("=" * 80)
print("Test Suite Complete")
print("=" * 80)
