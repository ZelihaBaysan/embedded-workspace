from jira_embedding import JiraEmbeddingMethod
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
        print(f"{tag} {i+1}: {doc.metadata.get('issue_key')}")


if __name__ == "__main__":
    load_dotenv()

    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("jira_issues")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    embedder = JiraEmbeddingMethod(
        jira_url=os.environ.get("JIRA_URL"),
        email=os.environ.get("JIRA_EMAIL"),
        api_token=os.environ.get("JIRA_API_TOKEN"),
        project_key="YOUR-PROJECT-KEY"
    )

    try:
        print("[index_task_001] Loading all issues...")
        documents = embedder.get_documents("jira_project")
        debug_print_docs(documents, "[LOADED]")

        print("\n[index_task_002] Applying regex filters...")
        documents = embedder.apply_rules(
            documents,
            inclusion_rules=[],  # boşsa hepsi dahil
            exclusion_rules=[
                r'^TEST-',  # TEST- prefixli issue'ları hariç tut
                r'-BUG$',   # -BUG suffixli issue'ları hariç tut
                r'^EPIC-'   # EPIC tipindeki issue'ları hariç tut
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