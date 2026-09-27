from typing import Dict, Any, List
from backend.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ResearchPlanner(BaseAgent):
    def __init__(self):
        super().__init__(role_name="Research Planner")

    def plan(self, query: str) -> Dict[str, Any]:
        system_prompt = (
            "You are an expert AI Research Planner. Your objective is to analyze a complex research query, "
            "break it down into 4-6 distinct, focused sub-topics, identify key technical areas to investigate, "
            "and produce a structured research plan."
        )
        prompt = (
            f"Research Question: '{query}'\n\n"
            "Break this question into key research sub-topics. For each sub-topic, provide a clear task description.\n"
            "Return JSON matching this exact structure:\n"
            "{\n"
            "  \"research_plan\": [\n"
            "    {\"topic\": \"Sub-topic Name\", \"description\": \"What to research in this area\", \"assigned_to\": \"Research Agent A\"}\n"
            "  ]\n"
            "}"
        )

        fallback = {
            "research_plan": [
                {
                    "topic": f"Current State & Foundations of {query}",
                    "description": f"Investigate present capabilities, technical benchmarks, and background of {query}.",
                    "assigned_to": "Research Agent A"
                },
                {
                    "topic": f"Key Technical Approaches & Architectures",
                    "description": f"Examine leading algorithmic methodologies, compute requirements, and paradigms related to {query}.",
                    "assigned_to": "Research Agent B"
                },
                {
                    "topic": f"Limitations, Safety & Governance",
                    "description": f"Analyze technical bottlenecks, safety alignment concerns, and societal considerations for {query}.",
                    "assigned_to": "Research Agent C"
                },
                {
                    "topic": f"Future Directions & Breakthrough Predictions",
                    "description": f"Identify emerging research trends, speculative timelines, and open questions regarding {query}.",
                    "assigned_to": "Research Agent D"
                }
            ]
        }

        res = self.generate_json(prompt, system_prompt, fallback_data=fallback)
        plan = res.get("research_plan")
        if not plan or not isinstance(plan, list):
            plan = fallback["research_plan"]

        return {
            "research_plan": plan,
            "tasks": [item["topic"] for item in plan]
        }
