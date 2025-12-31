from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os


def create_qa_chain(vectorstore):
    """
    Create a RetrievalQA chain with hallucination prevention.
    
    Args:
        vectorstore: Chroma vector store object
        
    Returns:
        RetrievalQA chain
    """
    # Initialize latest GPT-4 Turbo model
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Define prompt template with strict hallucination prevention
    template = """You are an expert assistant. Use ONLY the following context to answer the question.
If the answer is not explicitly present in the context, you MUST respond:
"I don't know based on the provided documents."

NEVER use outside knowledge. Answer ONLY from the context below.
Always cite the source document filename.

Context:
{context}

Question:
{question}

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
