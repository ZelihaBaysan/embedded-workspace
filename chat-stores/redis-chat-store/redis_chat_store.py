import re
from typing import List, Sequence, Optional, Pattern
from llama_index.core import Document
from llama_index.core.schema import BaseNode
import redis



class RedisChatStore:
    def __init__(
        self,
        host: str,
        port: int,
        password: Optional[str] = None,
        db: Optional[int] = 0,
        ssl: bool = False  
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.ssl = ssl  # <--- Upstash için eklendi

        self.redis_client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            ssl=ssl,  # <--- Upstash için eklendi
            decode_responses=True
        )

    @staticmethod
    def customize_metadata(document: Document, data_source_id: str) -> Document:
        document.metadata.update({
            "data_source_id": data_source_id,
            "file_type": document.metadata.get("file_name", "").split(".")[-1].lower()
        })
        return document

    def _compile_patterns(self, patterns: List[str]) -> List[Pattern]:
        compiled = []
        for pattern in patterns:
            try:
                compiled.append(re.compile(pattern))
            except re.error:
                print(f"Invalid regex pattern: {pattern}")
        return compiled

    def apply_rules(
        self,
        documents: Sequence[Document],
        inclusion_rules: List[str],
        exclusion_rules: List[str],
    ) -> Sequence[Document]:
        compiled_exclude = self._compile_patterns(exclusion_rules)
        compiled_include = self._compile_patterns(inclusion_rules)

        filtered_docs = []
        print("\n[apply_rules] Başlangıç doküman sayısı:", len(documents))

        for doc in documents:
            file_path = doc.metadata.get("file_path", "")
            excluded = any(pattern.search(file_path) for pattern in compiled_exclude)
            included = any(pattern.search(file_path) for pattern in compiled_include) if compiled_include else True

            if excluded:
                print(f"[apply_rules] Dışlandı: {file_path}")
                continue
            if not included:
                print(f"[apply_rules] Dahil edilmedi: {file_path}")
                continue

            print(f"[apply_rules] Geçti: {file_path}")
            filtered_docs.append(doc)

        return filtered_docs

    def get_documents(self, data_source_id: str) -> List[Document]:
        documents = []

        try:
            keys = self.redis_client.keys('*')

            for key in keys:
                try:
                    key_type = self.redis_client.type(key)

                    if key_type == 'string':
                        content = self.redis_client.get(key)
                    elif key_type == 'hash':
                        content = str(self.redis_client.hgetall(key))
                    elif key_type == 'list':
                        content = str(self.redis_client.lrange(key, 0, -1))
                    elif key_type == 'set':
                        content = str(self.redis_client.smembers(key))
                    elif key_type == 'zset':
                        content = str(self.redis_client.zrange(key, 0, -1))
                    else:
                        print(f"[get_documents] Desteklenmeyen veri tipi: {key_type} for key: {key}")
                        continue

                    doc = Document(
                        text=content,
                        metadata={
                            "file_path": key,
                            "file_name": key.split('/')[-1] if '/' in key else key,
                            "file_extension": "",
                            "last_modified": str(self.redis_client.ttl(key)) if self.redis_client.ttl(key) > 0 else "no_expiry"
                        }
                    )
                    self.customize_metadata(doc, data_source_id)
                    documents.append(doc)

                except Exception as e:
                    print(f"[get_documents] Error processing key {key}: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error accessing Redis: {str(e)}")
            return documents

        print(f"[get_documents] Toplam {len(documents)} doküman alındı")
        return documents

    def get_nodes(self, documents: Sequence[Document]) -> Sequence[BaseNode]:
        return []
