from langchain_google_genai import ChatGoogleGenerativeAI


def verify_answer(question: str, answer: str, source_docs: list) -> bool:
    """
    Verify that a generated answer is fully supported by source documents.
    
    This is a critical safety check to prevent hallucinations from reaching users.
    
    Args:
        question: The user's original question
        answer: The generated answer to verify
        source_docs: List of retrieved source documents
        
    Returns:
        True if answer is VALID (fully supported)
        False if answer is INVALID (contains unsupported claims)
    """
    # If no sources, answer cannot be valid
    if not source_docs or len(source_docs) == 0:
        return False
    
    # Extract text content from source documents
    source_texts = []
    for doc in source_docs:
        if hasattr(doc, 'page_content'):
            source_texts.append(doc.page_content)
        elif isinstance(doc, dict) and 'page_content' in doc:
            source_texts.append(doc['page_content'])
    
    # Combine all source texts
    combined_sources = "\n\n---\n\n".join(source_texts)
    
    # Initialize Gemini Pro with zero temperature for deterministic verification
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        temperature=0
    )
    
    # Strict verification prompt
    verification_prompt = f"""You are an enterprise AI safety verifier.

Task:
Verify whether the answer below is fully supported by the provided source documents.

Rules:
- If ANY claim in the answer is not directly supported by the sources, respond INVALID
- If ALL claims in the answer are directly supported by the sources, respond VALID
- Do NOT generate new information
- Do NOT re-answer the question
- Respond with ONE WORD ONLY: VALID or INVALID

Source Documents:
{combined_sources}

User Question:
{question}

Answer to Verify:
{answer}

Your verification (ONE WORD: VALID or INVALID):"""

    try:
        # Get verification decision from LLM
        response = llm.invoke(verification_prompt)
        
        # Extract and clean response
        decision = response.content.strip().upper()
        
        # Remove any punctuation or extra text
        decision = decision.replace(".", "").replace("!", "").replace("?", "")
        
        # Only accept exact match
        if decision == "VALID":
            return True
        elif decision == "INVALID":
            return False
        else:
            # If response is malformed, fail closed (default to INVALID)
            return False
            
    except Exception as e:
        # On any error, fail closed (default to INVALID for safety)
        return False


def extract_document_content(source_docs: list) -> str:
    """
    Helper function to extract readable content from source documents.
    
    Args:
        source_docs: List of source document objects
        
    Returns:
        Combined text content from all documents
    """
    if not source_docs:
        return ""
    
    contents = []
    for doc in source_docs:
        if hasattr(doc, 'page_content'):
            contents.append(doc.page_content)
        elif isinstance(doc, dict) and 'page_content' in doc:
            contents.append(doc['page_content'])
    
    return "\n\n".join(contents)
