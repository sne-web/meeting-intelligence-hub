import os
# Force cache directory to be local within the backend folder so it's always preserved in Render build image
os.environ["HF_HOME"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "hf_cache"))

print("Pre-downloading HuggingFace embedding model...")
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)
print("Model cached successfully!")
