import re
import os
from typing import List, Sequence, Pattern
from llama_index.core import Document
from llama_index.core.schema import BaseNode

class ObsidianEmbeddingMethod:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path

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
        # Varsayılan Obsidian özel dosya/dizinleri
        default_obsidian_exclusions = [
            r'(^|/)\.obsidian/',  # Obsidian ayar klasörü
            r'(^|/)\.trash/',     # Çöp klasörü
            r'\.DS_Store$',       # macOS sistem dosyası
            r'\.git/',            # Git klasörü
            r'Thumbs\.db$',       # Windows thumbnail dosyası
        ]

        # Kullanıcının verdiği kuralları varsayılanlarla birleştir
        combined_exclusions = default_obsidian_exclusions + exclusion_rules

        compiled_exclude = self._compile_patterns(combined_exclusions)
        compiled_include = self._compile_patterns(inclusion_rules)

        filtered_docs = []
        print("\n[apply_rules] Başlangıç doküman sayısı:", len(documents))

        for doc in documents:
            file_path = doc.metadata.get("file_path", "")
            file_ext = doc.metadata.get("file_extension", "")

            # Özel durum: .md uzantılı olmayanları hariç tut (isteğe bağlı)
            if file_ext != 'md':
                print(f"[apply_rules] Uzantı filtresi: {file_path} (.md dosyası değil)")
                continue

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

        for root, _, files in os.walk(self.vault_path):
            for file_name in files:
                if not file_name.lower().endswith(".md"):
                    continue

                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    print(f"[get_documents] Dosya okunamadı: {file_path}, Hata: {str(e)}")
                    continue

                file_ext = file_name.split('.')[-1].lower()

                doc = Document(
                    text=content,
                    metadata={
                        "file_path": file_path,
                        "file_name": file_name,
                        "file_extension": file_ext,
                        "last_modified": os.path.getmtime(file_path)
                    }
                )
                self.customize_metadata(doc, data_source_id)
                documents.append(doc)

        print(f"[get_documents] Toplam {len(documents)} dosya alındı")
        return documents

    def get_nodes(self, documents: Sequence[Document]) -> Sequence[BaseNode]:
        return []
