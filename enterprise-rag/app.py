import os
from dotenv import load_dotenv
from ingest.load_docs import load_and_chunk_documents
from rag.retriever import create_vectorstore, load_vectorstore
from rag.qa_chain import create_qa_chain


def format_sources(source_documents):
    """
    Format source documents for clean display.
    
    Args:
        source_documents: List of source documents
        
    Returns:
        Formatted string of sources
    """
    if not source_documents:
        return "None"
    
    sources = []
    seen = set()
    
    for doc in source_documents:
        source_file = os.path.basename(doc.metadata.get("source", "Unknown"))
        # Avoid duplicates
        if source_file not in seen:
            seen.add(source_file)
            sources.append(f"- {source_file}")
    
    return "\n".join(sources) if sources else "None"


def get_confidence(source_documents):
    """
    Calculate confidence level based on number of retrieved sources.
    
    Args:
        source_documents: List of source documents
        
    Returns:
        Confidence level string: High, Medium, or Low
    """
    num_sources = len(source_documents) if source_documents else 0
    
    if num_sources >= 2:
        return "High"
    elif num_sources == 1:
        return "Medium"
    else:
        return "Low"


def initialize_system():
    """
    Initialize the RAG system: load docs, create vectorstore, create QA chain.
    
    Returns:
        QA chain object
    """
    # Check if vectorstore exists
    vectorstore_path = "data/vectorstore"
    
    if os.path.exists(vectorstore_path) and os.listdir(vectorstore_path):
        print("Loading existing vector store...")
        vectorstore = load_vectorstore(vectorstore_path)
    else:
        print("Creating new vector store...")
        # Load and chunk documents
        documents = load_and_chunk_documents("data/raw")
        print(f"Loaded {len(documents)} document chunks")
        
        # Create vector store
        vectorstore = create_vectorstore(documents, vectorstore_path)
        print("Vector store created and persisted")
    
    # Create QA chain
    qa_chain = create_qa_chain(vectorstore)
    
    return qa_chain


def run_chatbot():
    """
    Run the CLI chatbot loop.
    """
    # Load environment variables
    load_dotenv()
    
    print("Initializing Enterprise RAG Chatbot...")
    print("=" * 60)
    
    # Initialize system
    qa_chain = initialize_system()
    
    print("\n" + "=" * 60)
    print("Chatbot ready! Ask questions about internal policies.")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 60 + "\n")
    
    # Chat loop
    while True:
        # Get user input
        question = input("You: ").strip()
        
        # Exit conditions
        if question.lower() in ["exit", "quit"]:
            print("\nGoodbye!")
            break
        
        if not question:
            continue
        
        # Get answer from QA chain
        try:
            result = qa_chain.invoke({"query": question})
            
            # Get source documents and calculate confidence
            source_docs = result.get("source_documents", [])
            confidence = get_confidence(source_docs)
            answer = result["result"]
            
            # Handle negative case - force "I don't know" for low confidence
            if confidence == "Low":
                answer = "I don't know based on the provided documents."
            
            # Print formatted output
            print("\nAnswer:")
            print(answer)
            
            print("\nSources:")
            print(format_sources(source_docs))
            
            print("\nConfidence:")
            print(confidence)
            
            print("\n" + "-" * 60 + "\n")
            
        except Exception as e:
            print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    run_chatbot()
