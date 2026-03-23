import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from services.claude_client import ask_claude

# Where ChromaDB stores its data on disk
CHROMA_DIR = "storage/chroma_db"

# Load the embedding model once when the module is imported.
# This model runs locally for free — no API needed.
# It converts text into vectors (lists of numbers) that represent meaning.
# Similar sentences will have similar vectors.
print("Loading embedding model... (first time may take a minute)")
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)
print("Embedding model loaded!")

def index_transcript(meeting_id: str, transcript_text: str):
    """
    Splits a transcript into chunks and stores them in ChromaDB.
    Called once when a transcript is first analysed.
    
    meeting_id      — unique ID so we can find this meeting's chunks later
    transcript_text — the full text of the transcript
    """
    
    # RecursiveCharacterTextSplitter splits text into overlapping chunks.
    # chunk_size=500 means each chunk is ~500 characters
    # chunk_overlap=50 means chunks share 50 characters with their neighbours
    # Overlap helps so context isn't lost at chunk boundaries
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    
    chunks = splitter.split_text(transcript_text)
    
    # Add meeting_id as metadata to every chunk
    # This lets us filter by meeting when searching
    metadatas = [{"meeting_id": meeting_id, "chunk_index": i} 
                 for i, _ in enumerate(chunks)]
    
    # Store in ChromaDB with a collection name based on meeting ID
    # Each meeting gets its own collection
    vectorstore = Chroma(
        collection_name=f"meeting_{meeting_id}",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )
    
    vectorstore.add_texts(texts=chunks, metadatas=metadatas)
    
    return len(chunks)


def query_transcripts(question: str, meeting_id: str = None) -> dict:
    """
    Searches through indexed transcripts to find relevant chunks,
    then asks the AI to answer the question using those chunks.
    
    question   — the user's question
    meeting_id — if provided, only search this meeting's transcript
                 if None, search across ALL meetings
    """
    
    # Build list of collections to search
    if meeting_id:
        collection_names = [f"meeting_{meeting_id}"]
    else:
        # Search all meetings — get all collection names from ChromaDB
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        collections = client.list_collections()
        collection_names = [c.name for c in collections]
    
    if not collection_names:
        return {
            "answer": "No transcripts have been indexed yet. Please analyse a meeting first.",
            "sources": []
        }
    
    # Search each collection and gather relevant chunks
    all_chunks = []
    sources = []
    
    for collection_name in collection_names:
        try:
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings,
                persist_directory=CHROMA_DIR
            )
            
            # similarity_search finds the top k most relevant chunks
            # It converts the question to a vector and finds similar vectors
            results = vectorstore.similarity_search(question, k=3)
            
            for doc in results:
                all_chunks.append(doc.page_content)
                sources.append({
                    "meeting_id": doc.metadata.get("meeting_id", "unknown"),
                    "chunk": doc.page_content[:100] + "..."
                })
        except Exception:
            continue
    
    if not all_chunks:
        return {
            "answer": "I couldn't find relevant information in the transcripts.",
            "sources": []
        }
    
    # Build context from retrieved chunks
    context = "\n\n---\n\n".join(all_chunks)
    
    # Ask the AI to answer based on the retrieved context
    prompt = f"""You are a helpful meeting assistant. Answer the user's question 
based ONLY on the meeting transcript excerpts provided below.

If the answer is not in the excerpts, say "I couldn't find that information 
in the available transcripts."

Always be specific and cite which part of the transcript supports your answer.

TRANSCRIPT EXCERPTS:
{context}

USER QUESTION:
{question}

Provide a clear, concise answer:"""

    answer = ask_claude(prompt, max_tokens=1000)
    
    return {
        "answer": answer,
        "sources": sources
    }