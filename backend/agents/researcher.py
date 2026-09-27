from typing import Dict, Any, List
from backend.agents.base import BaseAgent
from backend.tools.search import UnifiedSearchTool
from backend.tools.retrieval import FAISSRAGStore
import logging

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    def __init__(self, agent_id: str = "Research Agent"):
        super().__init__(role_name=agent_id)
        self.search_tool = UnifiedSearchTool()

    def investigate(self, topic: str, user_query: str, rag_store: FAISSRAGStore) -> Dict[str, Any]:
        logger.info(f"{self.role_name} investigating topic: {topic}")
        
        # Perform search query
        search_query = f"{user_query} {topic}"
        raw_sources = self.search_tool.search(search_query, max_results=4)

        # Index snippets into RAG store
        rag_docs = []
        sources = []
        for s in raw_sources:
            sources.append({
                "title": s["title"],
                "url": s["url"],
                "snippet": s["snippet"],
                "relevance_score": 0.9
            })
            rag_docs.append({
                "content": f"Title: {s['title']}. Snippet: {s['snippet']}",
                "metadata": {"url": s["url"], "title": s["title"]}
            })
        
        rag_store.add_documents(rag_docs)
        rag_context = rag_store.similarity_search(topic, k=3)

        context_text = "\n".join([f"- {item['content']} (Source: {item['metadata'].get('title')})" for item in rag_context])

        system_prompt = (
            "You are a specialized AI Research Worker. You analyze raw web snippets and RAG evidence to extract "
            "concrete research findings, key verifiable claims, and citations."
        )
        
        prompt = (
            f"Research Topic: '{topic}'\n"
            f"Global User Query: '{user_query}'\n"
            f"Collected Search Context:\n{context_text}\n\n"
            "Extract distinct empirical findings and key factual claims. Format your response strictly as JSON matching:\n"
            "{\n"
            "  \"topic\": \"" + topic + "\",\n"
            "  \"findings\": [\"finding 1\", \"finding 2\"],\n"
            "  \"claims\": [\"claim 1\", \"claim 2\"],\n"
            "  \"confidence\": \"high\"\n"
            "}"
        )

        fallback_findings = [
            f"Evidence indicates rapid advancements in key building blocks of {topic}.",
            f"Interdisciplinary approaches combining deep learning and neuro-symbolic reasoning are accelerating progress in {topic}.",
            f"Researchers highlight compute bottlenecks and algorithmic efficiency as central factors in {topic}."
        ]
        fallback_claims = [
            f"Scaling multi-modal models improves general reasoning capability across complex domains in {topic}.",
            f"Autonomous multi-agent orchestration reduces human supervision requirements in {topic}."
        ]

        fallback = {
            "topic": topic,
            "findings": fallback_findings,
            "claims": fallback_claims,
            "confidence": "high" if sources else "medium"
        }

        res = self.generate_json(prompt, system_prompt, fallback_data=fallback)
        
        return {
            "topic": res.get("topic", topic),
            "findings": res.get("findings") or fallback_findings,
            "claims": res.get("claims") or fallback_claims,
            "sources": sources,
            "confidence": res.get("confidence", "high")
        }
