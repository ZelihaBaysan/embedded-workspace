from ocr_embedding import DocumentEmbeddingMethod
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core import Settings
from llama_index.core.schema import MetadataMode
import chromadb
from dotenv import load_dotenv
import os

def debug_print_docs(docs, tag="[DEBUG]", max_print=5):
    print(f"\n{tag} Toplam {len(docs)} doküman (ilk {max_print} gösteriliyor):")
    for i, doc in enumerate(docs[:max_print]):
        metadata = doc.metadata
        print(f"{tag} {i+1}: {metadata.get('file_path')}")
        print(f"{tag}   - Tür: {metadata.get('file_type')}")
        print(f"{tag}   - Boyut: {metadata.get('file_size')} byte")
        print(f"{tag}   - Son değişiklik: {metadata.get('last_modified')}")

if __name__ == "__main__":
    load_dotenv()
    
    # LlamaCloud API anahtarı kontrolü
    if not os.getenv("LLAMA_CLOUD_API_KEY"):
        raise ValueError("LLAMA_CLOUD_API_KEY çevre değişkeni ayarlanmalıdır")

    # Global ayarları yapılandır
    Settings.chunk_size = 512
    Settings.chunk_overlap = 20

    # Embedding modeli
    embed_model = HuggingFaceEmbedding(
        model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2"),
        embed_batch_size=8
    )

    # ChromaDB ayarları
    db = chromadb.PersistentClient(path=os.getenv("CHROMA_DB_PATH", "./chroma_db"))
    chroma_collection = db.get_or_create_collection(
        os.getenv("CHROMA_COLLECTION_NAME", "llama_parsed_docs"),
        metadata={"hnsw:space": "cosine"}
    )
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # Doküman işleyiciyi oluştur
    embedder = DocumentEmbeddingMethod(
        docs_path=os.path.expanduser(os.getenv("DOCUMENTS_PATH", "./documents"))
    )

    try:
        # 1. Adım: Tüm dokümanları yükle
        print("\n[1/3] Dokümanlar yükleniyor...")
        documents = embedder.get_documents("llama_parsed_collection")
        debug_print_docs(documents, "[YÜKLENEN]")

        # 2. Adım: İşleme pipeline'ını oluştur
        print("\n[2/3] İşleme pipeline'ı hazırlanıyor...")
        node_parser = MarkdownNodeParser()
        
        pipeline = IngestionPipeline(
            transformations=[
                node_parser,
                embed_model
            ],
            vector_store=vector_store,
        )

        # 3. Adım: Dokümanları işle ve indeksle
        print("\n[3/3] Dokümanlar işleniyor ve indeksleniyor...")
        pipeline.run(
            documents=documents,
            show_progress=True,
            num_workers=4
        )
        
        # Sonuçları raporla
        print("\n[SONUÇ] İndeksleme tamamlandı:")
        print(f"- İşlenen toplam doküman: {len(documents)}")
        print(f"- Vektör koleksiyonundaki öğe sayısı: {chroma_collection.count()}")
        print("- Embedding modeli:", os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2"))
        print("- Kullanılan parser: LlamaParse")

    except Exception as e:
        print(f"\n[HATA] İşlem sırasında bir hata oluştu: {str(e)}")
        raise