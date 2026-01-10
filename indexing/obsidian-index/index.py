# index.py
from obsidian_embedding import ObsidianEmbeddingMethod
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
        print(f"{tag} {i+1}: {doc.metadata.get('file_path')} (Son değişiklik: {doc.metadata.get('last_modified', 'bilinmiyor')})")


if __name__ == "__main__":
    load_dotenv()

    # Embedding modeli (daha küçük boyutlu alternatifler de kullanılabilir)
    embed_model = HuggingFaceEmbedding(
        model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    )

    # ChromaDB ayarları
    db = chromadb.PersistentClient(path=os.getenv("CHROMA_DB_PATH", "./chroma_db"))
    chroma_collection = db.get_or_create_collection(
        os.getenv("CHROMA_COLLECTION_NAME", "obsidian_vaults")
    )
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # Obsidian embedder'ı oluşturma
    embedder = ObsidianEmbeddingMethod(
        vault_path=os.path.expanduser(os.getenv("OBSIDIAN_VAULT_PATH"))
    )

    try:
        print("\n[index_task_001] Loading all documents...")
        documents = embedder.get_documents("obsidian_vault")
        debug_print_docs(documents, "[LOADED]")

        print("\n[index_task_002] Applying filters...")
        documents = embedder.apply_rules(
            documents,
            inclusion_rules=[
                r'\.md$',  # Sadece markdown dosyalarını al
            ],
            exclusion_rules=[
                r'(^|/)\.obsidian/',  # Obsidian ayar klasörü
                r'(^|/)\.trash/',     # Çöp klasörü
                r'(^|/)\.git/',       # Git klasörü
                r'(^|/)temp/',        # Geçici klasör
                r'\/_',               # _ ile başlayan klasör/dosyalar
                r'\.(png|jpg|jpeg|pdf|drawio)$'  # Resim ve PDF dosyaları
            ]
        )
        debug_print_docs(documents, "[FILTERED]")

        print("\n[index_task_003] Creating vector index...")
        pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(
                    chunk_size=int(os.getenv("CHUNK_SIZE", "512")),
                    chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "20")),
                    # Obsidian'ın wikilink formatını dikkate alan ayar
                    paragraph_separator=r'\n\n|\n-{3,}\n|\[\[.*?\]\]'
                ),
                embed_model
            ],
            vector_store=vector_store,
        )

        # Dokümanları işleme ve indeksleme
        pipeline.run(documents=documents)
        
        print("\n[index_task_004] Indexing stats:")
        print(f"- Toplam doküman: {len(documents)}")
        print(f"- Vektör koleksiyonu boyutu: {chroma_collection.count()}")
        print("[SUCCESS] Indexing completed successfully ✅")

    except Exception as e:
        print(f"\n[ERROR] Indexing failed: {str(e)}")
        raise