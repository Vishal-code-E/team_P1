from langchain_openai import ChatOpenAI
import json
import os


def route_intent(user_query: str) -> dict:
    """
    Intent routing agent that decides how the system should respond.
    
    Returns one of three decisions:
    - RETRIEVE_AND_ANSWER: Query requires document retrieval
    - ANSWER_DIRECTLY: Conversational/meta query, no retrieval needed
    - REFUSE: Out-of-scope or speculative query
    
    Args:
        user_query: The user's input question
        
    Returns:
        dict with "decision" and "reason" keys
    """
    # Initialize OpenAI with zero temperature for deterministic routing
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Strict system prompt for intent classification
    system_prompt = """You are an enterprise AI intent router.
Your job is to decide how the system should respond to a user question.

Rules:
- Do NOT answer the question
- Do NOT retrieve documents
- ONLY decide the action

Decision types:
1. RETRIEVE_AND_ANSWER: Question is about internal company knowledge (policies, budgets, procedures) that likely exists in company documents
2. ANSWER_DIRECTLY: Conversational query, greeting, meta-question, or simple acknowledgment that does NOT require company documents
3. REFUSE: Out-of-scope, speculative, predictive, or questions that cannot be answered from internal knowledge

Return ONLY valid JSON in this exact format:
{
  "decision": "RETRIEVE_AND_ANSWER" | "ANSWER_DIRECTLY" | "REFUSE",
  "reason": "<short, factual explanation>"
}

NO extra text. NO markdown. JSON only."""

    # Construct the full prompt
    full_prompt = f"{system_prompt}\n\nUser query: {user_query}\n\nYour JSON response:"
    
    try:
        # Get LLM decision
        response = llm.invoke(full_prompt)
        
        # Extract text content
        response_text = response.content.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            # Remove ```json and ```
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            response_text = response_text.strip()
        
        # Parse JSON
        decision_data = json.loads(response_text)
        
        # Validate decision is one of the allowed values
        allowed_decisions = ["RETRIEVE_AND_ANSWER", "ANSWER_DIRECTLY", "REFUSE"]
        if decision_data.get("decision") not in allowed_decisions:
            # Default to REFUSE on invalid decision
            return {
                "decision": "REFUSE",
                "reason": "Invalid routing decision from agent"
            }
        
        return decision_data
        
    except (json.JSONDecodeError, KeyError, Exception) as e:
        # On any parsing failure, default to REFUSE for safety
        return {
            "decision": "REFUSE",
            "reason": f"Intent routing failed: {str(e)}"
        }


def get_direct_answer(user_query: str) -> str:
    """
    Generate a direct answer without document retrieval.
    Used for conversational queries (greetings, meta-questions).
    
    Args:
        user_query: The user's input question
        
    Returns:
        Direct response from LLM
    """
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    prompt = f"""You are a helpful enterprise assistant.
Provide a brief, professional response to this conversational query.
Keep it under 2 sentences.

User: {user_query}

Your response:"""
    
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return "I'm here to help with questions about internal company policies and documents."
