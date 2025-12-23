import os
from dotenv import load_dotenv
from ingest.load_docs import load_and_chunk_documents
from rag.retriever import create_vectorstore, load_vectorstore
from rag.qa_chain import create_qa_chain


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
            
            # Print answer
            print("\nANSWER:")
            print(result["result"])
            
            # Print sources
            print("\nSOURCES:")
            sources = set()
            for doc in result["source_documents"]:
                source_file = os.path.basename(doc.metadata.get("source", "Unknown"))
                sources.add(source_file)
            
            for source in sources:
                print(f"- {source}")
            
            print("\n" + "-" * 60 + "\n")
            
        except Exception as e:
            print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    run_chatbot()
