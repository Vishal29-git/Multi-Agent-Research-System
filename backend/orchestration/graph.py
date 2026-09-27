from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from backend.agents.planner import ResearchPlanner
from backend.agents.researcher import ResearchAgent
from backend.agents.fact_checker import FactChecker
from backend.agents.analyst import Analyst
from backend.agents.critic import Critic
from backend.agents.writer import ReportWriter
from backend.tools.retrieval import FAISSRAGStore
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class ResearchState(TypedDict):
    session_id: str
    query: str
    research_plan: List[Dict[str, Any]]
    tasks: List[str]
    findings: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    verified_claims: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    critic_feedback: Dict[str, Any]
    report: str
    status: str
    current_agent: str
    progress_percent: int
    iteration: int
    max_iterations: int
    status_callback: Any

# Global shared RAG store per session execution
rag_stores: Dict[str, FAISSRAGStore] = {}

def get_rag_store(session_id: str) -> FAISSRAGStore:
    if session_id not in rag_stores:
        rag_stores[session_id] = FAISSRAGStore()
    return rag_stores[session_id]

# --- Node Implementations ---

def planner_node(state: ResearchState) -> Dict[str, Any]:
    session_id = state["session_id"]
    query = state["query"]
    
    if state.get("status_callback"):
        state["status_callback"](session_id, "planner", "Research Planner", "Analyzing research prompt & generating sub-topics", 15)

    planner = ResearchPlanner()
    result = planner.plan(query)

    return {
        "research_plan": result["research_plan"],
        "tasks": result["tasks"],
        "current_agent": "Research Planner",
        "progress_percent": 25,
        "status": "running"
    }

def researcher_node(state: ResearchState) -> Dict[str, Any]:
    session_id = state["session_id"]
    query = state["query"]
    plan = state.get("research_plan", [])
    rag_store = get_rag_store(session_id)
    iteration = state.get("iteration", 1)

    if state.get("status_callback"):
        state["status_callback"](session_id, "researcher", "Research Agents", f"Executing web search & RAG indexing (Iteration {iteration})", 40)

    researcher = ResearchAgent()
    new_findings = []
    all_sources = list(state.get("sources", []))
    all_claims = []

    for item in plan:
        topic = item["topic"]
        res = researcher.investigate(topic, query, rag_store)
        new_findings.append(res)
        
        # Merge sources
        for src in res.get("sources", []):
            if not any(existing["url"] == src["url"] for existing in all_sources):
                all_sources.append(src)
        
        all_claims.extend(res.get("claims", []))

    existing_findings = list(state.get("findings", []))
    existing_findings.extend(new_findings)

    return {
        "findings": existing_findings,
        "sources": all_sources,
        "current_agent": "Research Agents",
        "progress_percent": 55,
        "status": "running"
    }

def fact_checker_node(state: ResearchState) -> Dict[str, Any]:
    session_id = state["session_id"]
    findings = state.get("findings", [])
    sources = state.get("sources", [])
    rag_store = get_rag_store(session_id)

    if state.get("status_callback"):
        state["status_callback"](session_id, "fact_checker", "Fact Checker", "Cross-referencing claims against source evidence", 70)

    all_claims = []
    for f in findings:
        all_claims.extend(f.get("claims", []))

    # De-duplicate claims
    unique_claims = list(set(all_claims))

    fact_checker = FactChecker()
    verified = fact_checker.verify_claims(unique_claims, sources, rag_store)

    return {
        "verified_claims": verified,
        "current_agent": "Fact Checker",
        "progress_percent": 75,
        "status": "running"
    }

def analyst_node(state: ResearchState) -> Dict[str, Any]:
    session_id = state["session_id"]
    query = state["query"]
    findings = state.get("findings", [])
    verified = state.get("verified_claims", [])

    if state.get("status_callback"):
        state["status_callback"](session_id, "analyst", "Analyst", "Synthesizing trends, structural patterns & trade-offs", 85)

    analyst = Analyst()
    analysis_result = analyst.analyze(query, findings, verified)

    return {
        "analysis": analysis_result,
        "current_agent": "Analyst",
        "progress_percent": 90,
        "status": "running"
    }

def critic_node(state: ResearchState) -> Dict[str, Any]:
    session_id = state["session_id"]
    query = state["query"]
    findings = state.get("findings", [])
    verified = state.get("verified_claims", [])
    analysis = state.get("analysis", {})
    iteration = state.get("iteration", 1)
    max_iterations = state.get("max_iterations", settings.MAX_ITERATIONS)

    if state.get("status_callback"):
        state["status_callback"](session_id, "critic", "Critic", f"Evaluating academic completeness (Iter {iteration}/{max_iterations})", 93)

    critic = Critic()
    critique_result = critic.evaluate(query, findings, verified, analysis, iteration, max_iterations)

    return {
        "critic_feedback": critique_result,
        "current_agent": "Critic",
        "progress_percent": 95,
        "status": "running"
    }

def writer_node(state: ResearchState) -> Dict[str, Any]:
    session_id = state["session_id"]
    query = state["query"]
    plan = state.get("research_plan", [])
    findings = state.get("findings", [])
    verified = state.get("verified_claims", [])
    analysis = state.get("analysis", {})
    sources = state.get("sources", [])
    critic_fb = state.get("critic_feedback", {})

    if state.get("status_callback"):
        state["status_callback"](session_id, "writer", "Report Writer", "Drafting structured markdown report with citations", 98)

    writer = ReportWriter()
    report_md = writer.generate_report(query, plan, findings, verified, analysis, sources, critic_fb)

    if state.get("status_callback"):
        state["status_callback"](session_id, "completed", "Report Writer", "Research completed successfully", 100)

    # Clean up RAG store memory
    if session_id in rag_stores:
        del rag_stores[session_id]

    return {
        "report": report_md,
        "current_agent": "Report Writer",
        "progress_percent": 100,
        "status": "completed"
    }

def should_continue(state: ResearchState) -> str:
    feedback = state.get("critic_feedback", {})
    iteration = state.get("iteration", 1)
    max_iterations = state.get("max_iterations", settings.MAX_ITERATIONS)

    if feedback.get("is_sufficient", True) or iteration >= max_iterations:
        logger.info("Critic approved research sufficiency -> proceeding to Report Writer")
        return "writer"
    else:
        logger.info(f"Critic requested additional research (Iteration {iteration} -> {iteration + 1})")
        state["iteration"] = iteration + 1
        return "researcher"

# --- Build LangGraph Workflow ---

def build_research_graph():
    workflow = StateGraph(ResearchState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("fact_checker", fact_checker_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("writer", writer_node)

    workflow.set_entry_point("planner")

    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "fact_checker")
    workflow.add_edge("fact_checker", "analyst")
    workflow.add_edge("analyst", "critic")

    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "writer": "writer",
            "researcher": "researcher"
        }
    )

    workflow.add_edge("writer", END)

    return workflow.compile()

research_app = build_research_graph()
