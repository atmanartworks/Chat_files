from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .llm import get_llm

def get_direct_generation_chain():
    """Get a chain for direct content generation without RAG."""
    llm = get_llm()
    
    # Ultra-short prompt for maximum speed
    prompt = ChatPromptTemplate.from_template(
        """{query}

Response:"""
    )
    
    chain = prompt | llm | StrOutputParser()
    return chain
