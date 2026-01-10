from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
import time

# === AYARLAR ===

# Local embedding modelini kullan
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5",
    device="cpu",
    embed_batch_size=2
)

# Ollama LLM ayarı
Settings.llm = Ollama(
    model="gemma:2b",
    request_timeout=120,
    num_gpu=0,
    num_thread=2,
    system_prompt = (
    "You are an assistant that answers questions directly based on the document contents. "
    "Only provide answers using the information stored in the 'storage' folder. "
    )

)

# === Index Yükleme ===
print("Daha önce oluşturulmuş index yükleniyor...")
storage_context = StorageContext.from_defaults(persist_dir="./storage")

index = load_index_from_storage(storage_context)

# Sorgu motoru
query_engine = index.as_query_engine(
    similarity_top_k=2,
    response_mode="compact",
    verbose=True
)

# === Sohbet Başlat ===
print("Belgelerle sohbet başlatıldı! (Çıkmak için 'exit' yazın)")

while True:
    user_input = input("\nSoru: ")
    if user_input.lower() == "exit":
        break
    try:
        start = time.time()
        response = query_engine.query(user_input)
        print("\nYanıt:", response)
        print(f"\n⏱ Süre: {time.time() - start:.2f} saniye")
    except Exception as e:
        print("⚠️ Hata:", str(e))
