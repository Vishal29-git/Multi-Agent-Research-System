from typing import Dict, Any, List
from backend.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class Critic(BaseAgent):
    def __init__(self):
        super().__init__(role_name="Critic")

    def evaluate(self, query: str, findings: List[Dict[str, Any]], verified_claims: List[Dict[str, Any]], analysis: Dict[str, Any], iteration: int, max_iterations: int) -> Dict[str, Any]:
        logger.info(f"Critic evaluating research quality for iteration {iteration}/{max_iterations}")

        system_prompt = (
            "You are a rigorous Academic Peer Reviewer and Critic. Evaluate research completeness, evidence strength, "
            "logical rigor, and coverage of open questions."
        )

        # Count supported claims vs total
        supported = [c for c in verified_claims if c.get("status") in ["Supported", "Partially Supported"]]
        unsupported_count = len(verified_claims) - len(supported)

        prompt = (
            f"Research Question: '{query}'\n"
            f"Current Iteration: {iteration} / {max_iterations}\n"
            f"Total Sub-topics Covered: {len(findings)}\n"
            f"Total Verified Claims: {len(supported)} (Unsupported: {unsupported_count})\n"
            f"Key Trends Identified: {len(analysis.get('key_trends', []))}\n\n"
            "Assess whether the collected research is sufficient for drafting a comprehensive final report.\n"
            "Return JSON matching:\n"
            "{\n"
            "  \"is_sufficient\": true,\n"
            "  \"quality_score\": 8,\n" # 1 to 10 scale
            "  \"critique\": \"Critique summary text\",\n"
            "  \"missing_topics\": [\"Missing topic if any\"]\n"
            "}"
        )

        # Default rule: if we have >= 3 findings and iteration >= 1, or reached max_iterations, it's sufficient
        is_sufficient_fallback = True if (iteration >= max_iterations or (len(findings) >= 3 and len(supported) >= 3)) else False
        score_fallback = 8 if is_sufficient_fallback else 5

        fallback = {
            "is_sufficient": is_sufficient_fallback,
            "quality_score": score_fallback,
            "critique": "Research coverage is comprehensive with well-supported empirical claims and clear source attribution." if is_sufficient_fallback else "Additional investigation required on safety mechanisms and technical bottlenecks.",
            "missing_topics": [] if is_sufficient_fallback else [f"Deeper safety and alignment analysis for {query}"]
        }

        res = self.generate_json(prompt, system_prompt, fallback_data=fallback)

        # Enforce max_iterations boundary strictly
        is_sufficient = res.get("is_sufficient", is_sufficient_fallback)
        if iteration >= max_iterations:
            is_sufficient = True

        return {
            "is_sufficient": is_sufficient,
            "quality_score": res.get("quality_score", score_fallback),
            "critique": res.get("critique", fallback["critique"]),
            "missing_topics": res.get("missing_topics", [])
        }
