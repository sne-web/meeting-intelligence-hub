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


def query_transcripts(question: str, accessible_meetings: list, supabase_client=None) -> dict:
    """
    Searches through indexed transcripts to find relevant chunks,
    then asks the AI to answer the question using those chunks.
    
    question   — the user's question
    accessible_meetings — list of dictionaries containing 'id' and 'filename' of allowed meetings
    supabase_client — optional Supabase client to fetch transcript texts and auto-index on demand
    """
    if not accessible_meetings:
        return {
            "answer": "No transcripts have been indexed yet. Please analyse a meeting first.",
            "sources": []
        }
        
    # Search each collection and gather relevant chunks
    all_chunks = []
    sources = []
    
    for meeting in accessible_meetings:
        meeting_id = meeting["id"]
        filename = meeting.get("filename", meeting_id)
        collection_name = f"meeting_{meeting_id}"
        try:
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings,
                persist_directory=CHROMA_DIR
            )
            
            # Check if this collection is empty/missing in local storage (e.g. after server reboot)
            try:
                item_count = vectorstore._collection.count()
            except Exception:
                item_count = 0

            if item_count == 0 and supabase_client is not None:
                # Fetch transcript text from Supabase
                res = supabase_client.table("meetings").select("transcript_text").eq("id", meeting_id).execute()
                if res.data:
                    transcript_text = res.data[0].get("transcript_text", "")
                    if transcript_text:
                        print(f"Collection {collection_name} is empty. Auto-indexing from Supabase...")
                        index_transcript(meeting_id, transcript_text)
                        # Re-instantiate to load newly added texts
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
                meeting_obj = next((m for m in accessible_meetings if m.get("id") == m_id), None)
                fname = meeting_obj.get("filename", m_id) if meeting_obj else m_id
                
                # Prepend the filename so the LLM knows the metadata!
                chunk_text = f"[Source Meeting File: '{fname}']\n{doc.page_content}"
                all_chunks.append(chunk_text)
                
                sources.append({
                    "meeting_id": m_id,
                    "filename": fname,
                    "chunk": doc.page_content[:100] + "..."
                })
        except Exception as e:
            print(f"Error searching Chroma collection {collection_name}: {e}")
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