from redis_chat_store import RedisChatStore
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
    chroma_collection = db.get_or_create_collection("redis_chat_data")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # Upstash ortam değişkenlerine göre yapılandırıldı
    redis_store = RedisChatStore(
        host=os.environ.get("UPSTASH_REDIS_HOST"),
        port=int(os.environ.get("UPSTASH_REDIS_PORT", 6379)),
        password=os.environ.get("UPSTASH_REDIS_PASSWORD"),
        ssl=True  # Upstash Redis bağlantısı için gereklidir
    )

    try:
        print("[index_task_001] Loading all data from Redis...")
        documents = redis_store.get_documents("redis_chat_data")
        debug_print_docs(documents, "[LOADED]")

        print("\n[index_task_002] Applying regex filters...")
        documents = redis_store.apply_rules(
            documents,
            inclusion_rules=[],  # boşsa hepsi dahil
            exclusion_rules=[
                r'^cache:',
                r'^session:',
                r'^temp_',
                r'\.bin$',
                r'^system:',
                r'^lock:',
                r'^queue:'
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
