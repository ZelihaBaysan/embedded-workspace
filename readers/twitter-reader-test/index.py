from twitter_embedding import TwitterEmbeddingMethod
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
        print(f"{tag} {i+1}: Tweet {doc.metadata.get('tweet_id')} - {doc.text[:50]}...")


if __name__ == "__main__":
    load_dotenv()

    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("twitter_tweets")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    embedder = TwitterEmbeddingMethod(
        consumer_key=os.environ.get("TWITTER_CONSUMER_KEY"),
        consumer_secret=os.environ.get("TWITTER_CONSUMER_SECRET"),
        access_token=os.environ.get("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.environ.get("TWITTER_ACCESS_TOKEN_SECRET"),
        username=os.environ.get("TWITTER_USERNAME")
    )

    try:
        print("[index_task_001] Loading all tweets...")
        documents = embedder.get_documents("twitter_data")
        debug_print_docs(documents, "[LOADED]")

        print("\n[index_task_002] Applying regex filters...")
        documents = embedder.apply_rules(
            documents,
            inclusion_rules=[],  # boşsa hepsi dahil
            exclusion_rules=[
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
                r'RT @',  # Retweets
                r'@[A-Za-z0-9_]+',  # Mentions
                r'#[A-Za-z0-9_]+'  # Hashtags
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