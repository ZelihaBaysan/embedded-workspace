# gitlab_embedding.py
from typing import List, Sequence, Optional
from llama_index.core import Document
from llama_index.core.schema import BaseNode
from gitlab import Gitlab


class GitLabEmbeddingMethod:
    def __init__(
        self,
        repo_url: str,
        private_token: str,
        branch: Optional[str] = "main",
        ignore_directories: Optional[List[str]] = None,
        ignore_file_extensions: Optional[List[str]] = None,
    ):
        self.repo_url = repo_url
        self.private_token = private_token
        self.branch = branch
        self.ignore_directories = ignore_directories or []
        self.ignore_file_extensions = ignore_file_extensions or []
        
        # Parse project path from URL
        if "https://gitlab.com/" in repo_url:
            self.project_path = repo_url.split("https://gitlab.com/")[1].rstrip("/")
        else:
            self.project_path = repo_url.split("https://")[1].split("/", 1)[1].rstrip("/")

    @staticmethod
    def customize_metadata(document: Document, data_source_id: str) -> Document:
        document.metadata = {
            "file_path": document.metadata.get("file_path", ""),
            "file_name": document.metadata.get("file_name", ""),
            "data_source_id": data_source_id,
        }
        return document

    def apply_rules(
        self,
        documents: Sequence[Document],
        inclusion_rules: List[str],
        exclusion_rules: List[str],
    ) -> Sequence[Document]:
        filtered_docs = []
        for doc in documents:
            file_path = doc.metadata.get("file_path", "").lower()
            file_name = doc.metadata.get("file_name", "").lower()

            # Exclusion kontrolü
            if any(excl.lower() in file_path or excl.lower() in file_name for excl in exclusion_rules):
                continue

            # Inclusion kontrolü (eğer inclusion_rules boşsa tümünü kabul et)
            if not inclusion_rules or any(incl.lower() in file_path or incl.lower() in file_name for incl in inclusion_rules):
                filtered_docs.append(doc)

        return filtered_docs

    def get_documents(self, data_source_id: str) -> List[Document]:
        gl = Gitlab('https://gitlab.com', private_token=self.private_token)
        project = gl.projects.get(self.project_path)
        
        documents = []
        
        # Recursively get all repository files
        items = project.repository_tree(ref=self.branch, recursive=True, all=True)
        
        for item in items:
            if item['type'] != 'blob':  # Skip directories
                continue
                
            file_path = item['path']
            file_name = item['name']
            file_extension = f".{file_name.split('.')[-1]}" if '.' in file_name else ""
            
            # Apply ignore rules
            if (any(ignore_dir in file_path for ignore_dir in self.ignore_directories) or
                file_extension in self.ignore_file_extensions):
                continue
                
            try:
                file_content = project.files.get(file_path, ref=self.branch).decode().decode('utf-8')
                
                doc = Document(
                    text=file_content,
                    metadata={
                        "file_path": file_path,
                        "file_name": file_name,
                    }
                )
                self.customize_metadata(doc, data_source_id)
                documents.append(doc)
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue
                
        return documents

    def get_nodes(self, documents: Sequence[Document]) -> Sequence[BaseNode]:
        # Default implementation as requested
        return []