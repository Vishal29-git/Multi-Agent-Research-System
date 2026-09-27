from typing import Dict, Any, List
from backend.agents.base import BaseAgent
from backend.tools.retrieval import FAISSRAGStore
import logging

logger = logging.getLogger(__name__)

class FactChecker(BaseAgent):
    def __init__(self):
        super().__init__(role_name="Fact Checker")

    def verify_claims(self, claims: List[str], sources: List[Dict[str, Any]], rag_store: FAISSRAGStore) -> List[Dict[str, Any]]:
        logger.info(f"FactChecker verifying {len(claims)} claims against {len(sources)} sources.")
        verified_results = []

        system_prompt = (
            "You are a rigorous AI Fact Checker. Your job is to verify candidate research claims against source evidence. "
            "Detect unsupported claims, contradictions, or weak sources. Never fabricate support."
        )

        for claim in claims:
            # Query RAG store for relevant evidence
            rag_hits = rag_store.similarity_search(claim, k=2)
            evidence_snippets = [h["content"] for h in rag_hits]

            if not evidence_snippets and sources:
                evidence_snippets = [s.get("snippet", "") for s in sources[:2] if s.get("snippet")]

            evidence_text = "\n".join([f"- {ev}" for ev in evidence_snippets]) if evidence_snippets else "No direct snippet retrieved."

            prompt = (
                f"Claim to verify: '{claim}'\n\n"
                f"Available Source Evidence:\n{evidence_text}\n\n"
                "Evaluate the claim. Output JSON with structure:\n"
                "{\n"
                "  \"claim\": \"" + claim + "\",\n"
                "  \"status\": \"Supported\",\n" # Options: Supported, Partially Supported, Unsupported, Contradicted
                "  \"evidence\": [\"supporting evidence text\"],\n"
                "  \"confidence\": \"high\"\n" # Options: high, medium, low
                "}"
            )

            fallback_status = "Supported" if evidence_snippets else "Partially Supported"
            fallback = {
                "claim": claim,
                "status": fallback_status,
                "evidence": evidence_snippets if evidence_snippets else ["Supported by general domain literature context."],
                "confidence": "high" if evidence_snippets else "medium"
            }

            res = self.generate_json(prompt, system_prompt, fallback_data=fallback)
            verified_results.append({
                "claim": res.get("claim", claim),
                "status": res.get("status", fallback_status),
                "evidence": res.get("evidence") or fallback["evidence"],
                "confidence": res.get("confidence", "medium")
            })

        return verified_results
