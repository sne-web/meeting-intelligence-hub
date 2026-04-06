import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from services.llm_client import ask_ai

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


def query_transcripts(question: str, meeting_id: str = None, user_id: str = None) -> dict:
    """
    Searches through indexed transcripts to find relevant chunks,
    then asks the AI to answer the question using those chunks.
    
    question   — the user's question
    meeting_id — if provided, only search this meeting's transcript
                 if None, search across ALL meetings
    user_id    — the authenticated user's ID
    """
    try:
        import os
        with open(os.path.join("storage", "meetings_store.json"), "r") as f:
            all_meetings = json.load(f)
    except:
        all_meetings = []
    
    # Build list of collections to search
    if meeting_id:
        meeting = next((m for m in all_meetings if m.get("id") == meeting_id and m.get("user_id") == user_id), None)
        if not meeting:
            return {"answer": "Meeting not found or you do not have permission to access it.", "sources": []}
        collection_names = [f"meeting_{meeting_id}"]
    else:
        if user_id:
            user_meetings = [m for m in all_meetings if m.get("user_id") == user_id]
            collection_names = [f"meeting_{m['id']}" for m in user_meetings]
        else:
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
    
    # Pre-loaded meetings map already hoisted to top of function
    
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
                m_id = doc.metadata.get("meeting_id", "unknown")
                meeting_obj = next((m for m in all_meetings if m.get("id") == m_id), None)
                fname = meeting_obj.get("filename", m_id) if meeting_obj else m_id
                
                # Prepend the filename so the LLM knows the metadata!
                chunk_text = f"[Source Meeting File: '{fname}']\n{doc.page_content}"
                all_chunks.append(chunk_text)
                
                sources.append({
                    "meeting_id": m_id,
                    "filename": fname,
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

CRITICAL INSTRUCTIONS:
1. Provide a clear, natural, and concise answer.
2. DO NOT quote people or use their names directly in your main answer (e.g., avoid saying "Sarah mentioned" or "John said"). Summarize the decisions or discussions objectively.
3. You MUST append exactly one citation at the very end of your response in this exact format: "(Supported by: <brief summary of evidence>, from meeting file '<filename>' indicating <brief summary of transcript part>)". Do not include literal quotes anywhere.

TRANSCRIPT EXCERPTS:
{context}

USER QUESTION:
{question}

Answer:"""

    answer = ask_ai(prompt, max_tokens=1000)
    
    return {
        "answer": answer,
        "sources": sources
    }