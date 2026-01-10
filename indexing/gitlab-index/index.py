# index.py
from gitlab_embedding import GitLabEmbeddingMethod
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
import chromadb
from dotenv import load_dotenv
import os


def debug_print_docs(docs, tag="[DEBUG]", max_print=10):
    print(f"{tag} Toplam {len(docs)} doküman:")
    for i, doc in enumerate(docs[:max_print]):
        print(f"{tag} {i+1}: {doc.metadata.get('file_path')}")


if __name__ == "__main__":
    load_dotenv()

    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("gitlab_repos")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    embedder = GitLabEmbeddingMethod(
        repo_url="https://gitlab.com/ZelihaBaysan/test-llm-repo-assistant",
        private_token=os.environ.get("GITLAB_TOKEN"),
        branch="main"
    )

    try:
        print("[index_task_001] Loading all documents...")
        documents = embedder.get_documents("test_repo")
        debug_print_docs(documents, "[LOADED]")

        print("\n[index_task_002] Applying regex filters...")
        documents = embedder.apply_rules(
            documents,
            inclusion_rules=[],  # boşsa hepsi dahil
            exclusion_rules=[
                r'(^|/)tests?/',
                r'__pycache__',
                r'\.md$',
                r'\.png$',
                r'\.jpg$',
                r'\.jpeg$'
            ]
        )
        debug_print_docs(documents, "[FILTERED]")

        print("\n[index_task_003] Creating vector index...")
        pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(chunk_size=512, chunk_overlap=20),
                embed_model
            ],
            vector_store=vector_store,
        )

        pipeline.run(documents=documents)
        print("[index_task_004] Indexing completed successfully ✅")

    except Exception as e:
        print(f"[ERROR] Indexing failed: {str(e)}")
        raise
