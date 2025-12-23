from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


def create_qa_chain(vectorstore):
    """
    Create a RetrievalQA chain with hallucination prevention.
    
    Args:
        vectorstore: Chroma vector store object
        
    Returns:
        RetrievalQA chain
    """
    # Initialize ChatOpenAI with gpt-3.5-turbo
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0
    )
    
    # Define prompt template with hallucination prevention
    template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer based on the context provided, just say "I don't know". 
Do not try to make up an answer.
Always provide the answer based strictly on the given context.

Context: {context}

Question: {question}

Answer:"""
    
    PROMPT = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    
    # Create RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    return qa_chain
