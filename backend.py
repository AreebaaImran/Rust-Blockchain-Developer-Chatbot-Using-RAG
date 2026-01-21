from config import embeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from pathlib import Path
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import FileChatMessageHistory

# Load Vector Store

vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

# Initialize LLM

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --------  Prompt Templates  --------

# Query rewriter (for history-aware retrieval)

CONDENSE_QUESTION_SYSTEM = """\
You are a query rewriting assistant for a RAG chatbot about Rust, Cosmos SDK, CosmWasm, and Osmosis.
Rewrite the user's latest question into a **standalone** search query, incorporating relevant details from the chat history.
Do NOT answer; only output the rewritten query.
"""

condense_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", CONDENSE_QUESTION_SYSTEM),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ]
)

# Answering prompt (stuff docs chain)

ANSWER_SYSTEM = """\
You are a precise assistant that explains blockchain theory, Rust, Cosmos SDK, and CosmWasm concepts and code.

Rules:
- Use only the provided CONTEXT. If not found, say so.
- For CosmWasm or Rust code, explain step by step with small code excerpts in triple backticks.
- Cite sources (metadata like file path, URL, or source+page) as markdown footnotes.
- If helpful, suggest "Next steps".
"""

ANSWER_HUMAN = """\
Question: {input}

CONTEXT:
{context}

(You may also use chat history above.)
"""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ANSWER_SYSTEM),
        MessagesPlaceholder("chat_history"),
        ("human", ANSWER_HUMAN),
    ]
)

# --------  Retrieval and Document QA  --------

# Document QA chain (stuff docs) 
doc_chain = create_stuff_documents_chain(llm, qa_prompt)

# Retriever 
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 6,
        "fetch_k": 30,
    },
)

# History-aware retriever
history_aware_retriever = create_history_aware_retriever(
    llm=llm,
    retriever=retriever,
    prompt=condense_prompt,
)

# Full RAG chain (retrieval + doc QA)
rag_chain = create_retrieval_chain(history_aware_retriever, doc_chain)

# --------  Persistent chat history   --------

Path("chat_histories").mkdir(parents=True, exist_ok=True)
session_id = "demo-session"
chat_history = FileChatMessageHistory(file_path=f"chat_histories/{session_id}.json")

rag_with_history = RunnableWithMessageHistory(
    rag_chain,
    lambda session_id: FileChatMessageHistory(
        file_path=f"chat_histories/{session_id}.json"
    ),
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)