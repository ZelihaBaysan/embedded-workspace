import re
from typing import List, Sequence, Optional, Pattern
from llama_index.core import Document
from llama_index.core.schema import BaseNode
from jira import JIRA


class JiraEmbeddingMethod:
    def __init__(
        self,
        jira_url: str,
        email: str,
        api_token: str,
        project_key: str,
    ):
        self.jira_url = jira_url
        self.email = email
        self.api_token = api_token
        self.project_key = project_key

    @staticmethod
    def customize_metadata(document: Document, data_source_id: str) -> Document:
        document.metadata.update({
            "data_source_id": data_source_id,
            "issue_type": document.metadata.get("issue_type", "").lower()
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
            issue_key = doc.metadata.get("issue_key", "")
            excluded = any(pattern.search(issue_key) for pattern in compiled_exclude)
            included = any(pattern.search(issue_key) for pattern in compiled_include) if compiled_include else True

            if excluded:
                print(f"[apply_rules] Dışlandı: {issue_key}")
                continue
            if not included:
                print(f"[apply_rules] Dahil edilmedi: {issue_key}")
                continue

            print(f"[apply_rules] Geçti: {issue_key}")
            filtered_docs.append(doc)

        return filtered_docs

    def get_documents(self, data_source_id: str) -> List[Document]:
        jira = JIRA(
            server=self.jira_url,
            basic_auth=(self.email, self.api_token)
        )
        documents = []

        try:
            # Get all issues from the project
            issues = jira.search_issues(f'project={self.project_key}', maxResults=False)
        except Exception as e:
            print(f"Error accessing Jira: {str(e)}")
            return documents

        for issue in issues:
            try:
                # Get full issue details
                full_issue = jira.issue(issue.key)
                
                # Create document content
                content = f"""
                Issue Key: {issue.key}
                Summary: {issue.fields.summary}
                Description: {issue.fields.description}
                Issue Type: {issue.fields.issuetype.name}
                Status: {issue.fields.status.name}
                Created: {issue.fields.created}
                Updated: {issue.fields.updated}
                """.strip()

                doc = Document(
                    text=content,
                    metadata={
                        "issue_key": issue.key,
                        "summary": issue.fields.summary,
                        "issue_type": issue.fields.issuetype.name,
                        "status": issue.fields.status.name,
                        "created": issue.fields.created,
                        "updated": issue.fields.updated,
                        "assignee": getattr(issue.fields.assignee, 'displayName', None),
                        "reporter": getattr(issue.fields.reporter, 'displayName', None)
                    }
                )
                self.customize_metadata(doc, data_source_id)
                documents.append(doc)

            except Exception as e:
                print(f"[get_documents] Error processing issue {issue.key}: {str(e)}")
                continue

        print(f"[get_documents] Toplam {len(documents)} issue alındı")
        return documents

    def get_nodes(self, documents: Sequence[Document]) -> Sequence[BaseNode]:
        return []