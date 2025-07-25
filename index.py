# index.py
from gitlab_embedding import GitLabEmbeddingMethod
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
import chromadb
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    
    # Embedding model
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # ChromaDB setup
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("gitlab_repos")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # Indexing
    embedder = GitLabEmbeddingMethod(
        repo_url="https://gitlab.com/ZelihaBaysan/test-llm-repo-assistant",
        private_token=os.environ.get("GITLAB_TOKEN"),
        branch="main",
        ignore_directories=["node_modules", "dist", "tests"],
        ignore_file_extensions=[".png", ".jpg", ".md"]
    )

    try:
        # Pipeline
        pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(chunk_size=512, chunk_overlap=20),
                embed_model
            ],
            vector_store=vector_store,
        )

        print("[index_task_001] Loading documents...")
        documents = embedder.get_documents("test_repo")
        print(f"[index_task_001] {len(documents)} documents loaded")

        documents = embedder.apply_rules(
            documents,
            inclusion_rules=[],  
            exclusion_rules=["test"]  
        )
        print(f"[index_task_001] {len(documents)} documents after filtering")

        print("[index_task_001] Creating nodes and adding to vector store...")
        pipeline.run(documents=documents)
        
        print("[index_task_001] Indexing completed")
    except Exception as e:
        print(f"Indexing error: {str(e)}")