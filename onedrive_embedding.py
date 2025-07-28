import re
from typing import List, Sequence, Optional, Pattern
from llama_index.core import Document
from llama_index.core.schema import BaseNode
from msal import ConfidentialClientApplication
import requests

class OneDriveEmbeddingMethod:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        refresh_token: str,
        tenant_id: str,
    ):
        """
        OneDrive bağlantısı için güncel MSAL tabanlı init metodu
        
        Args:
            client_id: Azure AD uygulama kayıt client_id
            client_secret: Azure AD uygulama secret
            redirect_uri: Uygulama redirect URI (ör: http://localhost:8080)
            refresh_token: Kullanıcı refresh token
            tenant_id: Azure AD tenant ID (ör: "organizations" veya tenant GUID)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token
        self.tenant_id = tenant_id
        self.scopes = ["https://graph.microsoft.com/.default"]
        
        # MSAL Confidential Client uygulamasını oluştur
        self.app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )
        
        # Access token al
        self.access_token = self._get_access_token()
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def _get_access_token(self) -> str:
        """Refresh token kullanarak yeni bir access token alır"""
        try:
            result = self.app.acquire_token_by_refresh_token(
                refresh_token=self.refresh_token,
                scopes=self.scopes
            )
            if "access_token" not in result:
                raise Exception(f"Access token alınamadı: {result.get('error_description')}")
            return result["access_token"]
        except Exception as e:
            raise Exception(f"Token alma hatası: {str(e)}")

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
        inclusion_rules: Optional[List[str]] = None,
        exclusion_rules: Optional[List[str]] = None,
    ) -> Sequence[Document]:
        inclusion_rules = inclusion_rules or []
        exclusion_rules = exclusion_rules or []
        
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

    def _make_graph_api_request(self, url: str) -> dict:
        try:
            response = requests.get(
                url,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Graph API request failed: {str(e)}")

    def get_documents(self, data_source_id: str) -> List[Document]:
        documents = []

        try:
            # Graph API endpoint for root children
            url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
            items_data = self._make_graph_api_request(url)
            items = items_data.get('value', [])
        except Exception as e:
            print(f"Error accessing OneDrive: {str(e)}")
            return documents

        for item in items:
            if 'file' not in item:
                continue

            file_path = item.get('name', '')
            file_name = item.get('name', '')
            file_ext = file_name.split('.')[-1].lower() if '.' in file_name else ''

            try:
                # Get file content
                download_url = item.get('@microsoft.graph.downloadUrl')
                if not download_url:
                    print(f"[get_documents] Download URL not available for: {file_path}")
                    continue

                content_response = requests.get(download_url)
                content_response.raise_for_status()
                content = content_response.content

                if isinstance(content, bytes):
                    try:
                        content = content.decode('utf-8')
                    except UnicodeDecodeError:
                        print(f"[get_documents] Binary file skipped: {file_path}")
                        continue

                doc = Document(
                    text=content,
                    metadata={
                        "file_path": file_path,
                        "file_name": file_name,
                        "file_extension": file_ext,
                        "last_modified": item.get('lastModifiedDateTime', '')
                    }
                )
                self.customize_metadata(doc, data_source_id)
                documents.append(doc)

            except Exception as e:
                print(f"[get_documents] Error processing {file_path}: {str(e)}")
                continue

        print(f"[get_documents] Toplam {len(documents)} dosya alındı")
        return documents

    def get_nodes(self, documents: Sequence[Document]) -> Sequence[BaseNode]:
        return []