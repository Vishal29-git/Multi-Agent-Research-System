from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SimpleDocument:
    def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

class FAISSRAGStore:
    def __init__(self):
        self.documents: List[SimpleDocument] = []
        self.vectorstore = None
        self.embeddings = None
        self._init_embeddings()

    def _init_embeddings(self):
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            logger.info("Initialized HuggingFaceEmbeddings (all-MiniLM-L6-v2)")
        except Exception as e:
            logger.warning(f"Could not load HuggingFaceEmbeddings: {e}. Using simple keyword RAG fallback.")
            self.embeddings = None

    def add_documents(self, docs: List[Dict[str, Any]]):
        """
        Add documents list [{"content": ..., "metadata": ...}] to RAG store
        """
        new_docs = []
        for d in docs:
            content = d.get("content") or d.get("snippet") or ""
            metadata = d.get("metadata") or {"url": d.get("url", ""), "title": d.get("title", "")}
            if content:
                doc_obj = SimpleDocument(page_content=content, metadata=metadata)
                self.documents.append(doc_obj)
                new_docs.append(doc_obj)

        if not new_docs:
            return

        if self.embeddings:
            try:
                from langchain_community.vectorstores import FAISS
                from langchain_core.documents import Document as LCDocument
                
                lc_docs = [LCDocument(page_content=d.page_content, metadata=d.metadata) for d in new_docs]
                if self.vectorstore is None:
                    self.vectorstore = FAISS.from_documents(lc_docs, self.embeddings)
                else:
                    self.vectorstore.add_documents(lc_docs)
            except Exception as e:
                logger.warning(f"Failed to add to FAISS vectorstore: {e}")

    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Query vectorstore or keyword index for top k relevant passages
        """
        results = []
        if self.vectorstore and self.embeddings:
            try:
                hits = self.vectorstore.similarity_search(query, k=k)
                for h in hits:
                    results.append({
                        "content": h.page_content,
                        "metadata": h.metadata
                    })
                return results
            except Exception as e:
                logger.warning(f"FAISS similarity search error: {e}")

        # Simple keyword relevance fallback
        query_words = set(query.lower().split())
        scored = []
        for doc in self.documents:
            words = set(doc.page_content.lower().split())
            score = len(query_words.intersection(words))
            scored.append((score, doc))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        for _, doc in scored[:k]:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        return results
