import re
from typing import List, Sequence, Optional, Pattern
from llama_index.core import Document
from llama_index.core.schema import BaseNode
import tweepy


class TwitterEmbeddingMethod:
    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        access_token: str,
        access_token_secret: str,
        username: str,
    ):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.username = username

    @staticmethod
    def customize_metadata(document: Document, data_source_id: str) -> Document:
        document.metadata.update({
            "data_source_id": data_source_id,
            "content_type": document.metadata.get("content_type", "tweet")
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
            tweet_id = doc.metadata.get("tweet_id", "")
            tweet_text = doc.metadata.get("text", "")
            excluded = any(pattern.search(tweet_text) for pattern in compiled_exclude)
            included = any(pattern.search(tweet_text) for pattern in compiled_include) if compiled_include else True

            if excluded:
                print(f"[apply_rules] Dışlandı: {tweet_id}")
                continue
            if not included:
                print(f"[apply_rules] Dahil edilmedi: {tweet_id}")
                continue

            print(f"[apply_rules] Geçti: {tweet_id}")
            filtered_docs.append(doc)

        return filtered_docs

    def get_documents(self, data_source_id: str) -> List[Document]:
        auth = tweepy.OAuth1UserHandler(
            self.consumer_key,
            self.consumer_secret,
            self.access_token,
            self.access_token_secret
        )
        api = tweepy.API(auth)
        documents = []

        try:
            tweets = api.user_timeline(screen_name=self.username, count=200, tweet_mode="extended")
        except Exception as e:
            print(f"Error accessing Twitter API: {str(e)}")
            return documents

        for tweet in tweets:
            try:
                content = tweet.full_text
                if hasattr(tweet, 'retweeted_status'):
                    content = f"RT @{tweet.retweeted_status.user.screen_name}: {tweet.retweeted_status.full_text}"

                doc = Document(
                    text=content,
                    metadata={
                        "tweet_id": tweet.id_str,
                        "created_at": tweet.created_at.isoformat(),
                        "user": tweet.user.screen_name,
                        "retweet_count": tweet.retweet_count,
                        "favorite_count": tweet.favorite_count,
                        "content_type": "retweet" if hasattr(tweet, 'retweeted_status') else "tweet"
                    }
                )
                self.customize_metadata(doc, data_source_id)
                documents.append(doc)

            except Exception as e:
                print(f"[get_documents] Error processing tweet {tweet.id_str}: {str(e)}")
                continue

        print(f"[get_documents] Toplam {len(documents)} tweet alındı")
        return documents

    def get_nodes(self, documents: Sequence[Document]) -> Sequence[BaseNode]:
        return []