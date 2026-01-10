from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.node_parser import SentenceSplitter
import os
import torch

# Bellek optimizasyonu
torch.set_num_threads(2)  # CPU thread sayısını sınırla
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Paralel işlemi kapat

# Embedding modeli - Küçük boyutlu ve verimli
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5",
    device="cpu",  # GPU kullanma
    embed_batch_size=2  # Küçük batch boyutu
)

# Hafif Ollama modeli
Settings.llm = Ollama(
    model="gemma:2b",  # Daha küçük model
    request_timeout=120,  # Uzun timeout
    num_gpu=0,  # GPU kullanma
    system_prompt="Sen Türkçe konuşan bir belge asistanısın. Kullanıcı PDF, Word, metin belgeleri yükler. Onlara bu belgelerle ilgili özetler ve içerik verirken Türkçe ve doğal şekilde konuş."
)

# Belgeleri parçalara ayırarak yükle
print("Belgeler yükleniyor ve parçalara ayrılıyor...")
documents = SimpleDirectoryReader(
    "data",
    required_exts=[".pdf", ".txt", ".docx"]  # Sadece desteklenen formatlar
).load_data()

# Metin parçalayıcı - Küçük parçalar oluştur
splitter = SentenceSplitter(
    chunk_size=256,  # Küçük parça boyutu
    chunk_overlap=20
)
nodes = splitter.get_nodes_from_documents(documents)
print(f"Oluşturulan parça sayısı: {len(nodes)}")

# Index'i oluştur
print("Index oluşturuluyor...")
index = VectorStoreIndex(nodes)

# Index'i kaydet (isteğe bağlı)
storage_context = StorageContext.from_defaults()
storage_context.docstore.add_documents(nodes)
index.storage_context.persist(persist_dir="./storage")
print("Index 'storage' klasörüne kaydedildi")

# Basit sorgu motoru
query_engine = index.as_query_engine(
    similarity_top_k=2,  # Sadece 2 benzer sonuç
    response_mode="compact"  # Minimal yanıt modu
)

try:
    # Sorguyu dene
    print("\nSorgu çalıştırılıyor...")
    response = query_engine.query("PDF dosyasında ne yazıyor?")
    print("\nYanıt:", response)
except Exception as e:
    print("\nSorgu hatası:", str(e))
    print("\nİlk parçanın içeriği:")
    print(nodes[0].text[:500] + "...")  # İlk parçayı göster
    
    # Alternatif: Tüm belge içeriğini bas
    print("\nTüm belgelerin içeriği:")
    for i, doc in enumerate(documents):
        print(f"\nBelge {i+1} (İlk 300 karakter):")
        print(doc.text[:300] + "...")

print("\nİşlem tamamlandı")