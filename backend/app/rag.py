from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from .llm import get_llm

def get_qa_chain(vectorstore):
    llm = get_llm()
    # Optimize retriever for speed: fewer docs, shorter chunks
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}  # Only retrieve top 3 most relevant chunks (faster)
    )
    
    # Prompt with citation instructions (ChatGPT style)
    prompt = ChatPromptTemplate.from_template(
        """You are answering a question based on the provided context. Use inline citations like [1], [2], [3] in your response when referencing information.

Context: {context}

Question: {question}

Instructions:
- Include citation numbers [1], [2], [3] inline where you reference information
- Place citations immediately after the relevant information
- Be concise and natural

Answer:"""
    )
    
    # Create the chain using LCEL (LangChain Expression Language)
    def format_docs(docs):
        # Format with citation numbers (ChatGPT style)
        formatted = []
        for i, doc in enumerate(docs[:3], 1):
            formatted.append(f"[{i}] {doc.page_content[:500]}")
        return "\n\n".join(formatted)
    
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

def get_answer_with_sources(vectorstore, question: str):
    """
    Get answer with source documents for citations (ChatGPT-style inline citations).
    
    Args:
        vectorstore: The vector store
        question: User's question
    
    Returns:
        Dictionary with 'answer' and 'sources'
    """
    llm = get_llm()
    
    # Get relevant documents directly from vectorstore (more reliable)
    try:
        # Use similarity_search directly from vectorstore
        source_docs = vectorstore.similarity_search(question, k=3)
    except Exception as e1:
        try:
            # Fallback: use retriever with invoke()
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            source_docs = retriever.invoke(question)
            # Ensure it's a list
            if not isinstance(source_docs, list):
                source_docs = list(source_docs) if source_docs else []
        except Exception as e2:
            # Last resort: empty list
            print(f"Error retrieving documents: {e1}, {e2}")
            source_docs = []
    
    # Format context with citation numbers (ChatGPT style)
    context_parts = []
    for i, doc in enumerate(source_docs[:3], 1):
        content = doc.page_content[:500]
        context_parts.append(f"[{i}] {content}")
    
    context = "\n\n".join(context_parts) if context_parts else ""
    
    # Get answer with instruction to use inline citations
    prompt = ChatPromptTemplate.from_template(
        """You are answering a question based on the provided context. Use inline citations like [1], [2], [3] in your response when referencing information from the context.

Context:
{context}

Question: {question}

Instructions:
- Include citation numbers [1], [2], [3] inline in your response where you reference information
- Use [1] for the first source, [2] for the second, [3] for the third
- Place citations immediately after the relevant information
- Be natural and conversational

Answer:"""
    )
    
    answer = llm.invoke(prompt.format(context=context, question=question))
    answer_text = answer.content if hasattr(answer, 'content') else str(answer)
    
    return {
        "answer": answer_text,
        "sources": source_docs
    }
