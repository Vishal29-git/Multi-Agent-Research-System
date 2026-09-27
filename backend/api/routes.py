from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio
import json
import logging

from backend.database.session import get_db, SessionLocal
from backend.models.research import ResearchSession, Source, VerifiedClaim, ResearchFinding, ResearchTask
from backend.schemas.research import (
    ResearchRequest, SessionStatusResponse, SessionDetailResponse,
    SessionSummaryResponse, SourceSchema, AgentStatusSchema
)
from backend.orchestration.graph import research_app
from backend.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])

# In-memory store for active SSE event queues
sse_queues: Dict[str, List[asyncio.Queue]] = {}

def broadcast_sse_event(session_id: str, event_data: dict):
    if session_id in sse_queues:
        for q in sse_queues[session_id]:
            try:
                q.put_nowait(event_data)
            except Exception as e:
                logger.warning(f"Error pushing SSE event: {e}")

def update_session_status(session_id: str, agent_key: str, agent_name: str, activity: str, progress: int):
    db = SessionLocal()
    try:
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        if session:
            session.current_agent = agent_name
            session.progress_percent = progress
            if progress >= 100:
                session.status = "completed"
            elif session.status == "queued":
                session.status = "running"
            db.commit()

        # Broadcast live status update via SSE
        event_payload = {
            "session_id": session_id,
            "agent_key": agent_key,
            "agent_name": agent_name,
            "activity": activity,
            "progress": progress,
            "status": session.status if session else "running"
        }
        broadcast_sse_event(session_id, event_payload)
    except Exception as e:
        logger.error(f"Error updating session status in DB: {e}")
    finally:
        db.close()

def run_research_background(session_id: str, query: str):
    logger.info(f"Starting background research execution for session {session_id}")
    initial_state = {
        "session_id": session_id,
        "query": query,
        "research_plan": [],
        "tasks": [],
        "findings": [],
        "sources": [],
        "verified_claims": [],
        "analysis": {},
        "critic_feedback": {},
        "report": "",
        "status": "running",
        "current_agent": "Research Planner",
        "progress_percent": 5,
        "iteration": 1,
        "max_iterations": settings.MAX_ITERATIONS,
        "status_callback": update_session_status
    }

    try:
        final_state = research_app.invoke(initial_state)

        # Save results to DB
        db = SessionLocal()
        try:
            session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
            if session:
                session.report_markdown = final_state.get("report", "")
                session.status = "completed"
                session.progress_percent = 100
                session.current_agent = "Report Writer"

                # Save Sources
                for s in final_state.get("sources", []):
                    src_obj = Source(
                        session_id=session_id,
                        title=s.get("title", "Untitled Source"),
                        url=s.get("url", "#"),
                        snippet=s.get("snippet", ""),
                        relevance_score=s.get("relevance_score", 1.0)
                    )
                    db.add(src_obj)

                # Save Verified Claims
                for c in final_state.get("verified_claims", []):
                    claim_obj = VerifiedClaim(
                        session_id=session_id,
                        claim=c.get("claim", ""),
                        status=c.get("status", "Supported"),
                        evidence_json=c.get("evidence", []),
                        confidence=c.get("confidence", "medium")
                    )
                    db.add(claim_obj)

                # Save Findings
                for f in final_state.get("findings", []):
                    finding_obj = ResearchFinding(
                        session_id=session_id,
                        topic=f.get("topic", "General"),
                        findings_json=f.get("findings", []),
                        claims_json=f.get("claims", []),
                        sources_json=f.get("sources", []),
                        confidence=f.get("confidence", "medium")
                    )
                    db.add(finding_obj)

                db.commit()

            broadcast_sse_event(session_id, {
                "session_id": session_id,
                "agent_name": "Report Writer",
                "activity": "Research completed successfully!",
                "progress": 100,
                "status": "completed"
            })
        except Exception as db_err:
            logger.error(f"Failed to persist research results: {db_err}")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error during research execution for session {session_id}: {e}", exc_info=True)
        db = SessionLocal()
        try:
            session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
            if session:
                session.status = "failed"
                session.error_message = str(e)
                db.commit()
            broadcast_sse_event(session_id, {
                "session_id": session_id,
                "status": "failed",
                "error": str(e)
            })
        finally:
            db.close()


@router.post("", response_model=SessionSummaryResponse)
def start_research(req: ResearchRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Research query cannot be empty.")

    session = ResearchSession(
        query=req.query.strip(),
        status="queued",
        current_agent="Research Planner",
        progress_percent=0
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    background_tasks.add_task(run_research_background, session.id, session.query)

    return session


@router.get("", response_model=List[SessionSummaryResponse])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(ResearchSession).order_by(ResearchSession.created_at.desc()).all()
    return sessions


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found.")
    
    sources = db.query(Source).filter(Source.session_id == session_id).all()
    claims = db.query(VerifiedClaim).filter(VerifiedClaim.session_id == session_id).all()

    return {
        "id": session.id,
        "query": session.query,
        "status": session.status,
        "progress_percent": session.progress_percent,
        "iterations": session.iterations,
        "report_markdown": session.report_markdown,
        "sources": [SourceSchema.model_validate(s) for s in sources],
        "claims": [
            {
                "id": c.id,
                "claim": c.claim,
                "status": c.status,
                "evidence": c.evidence_json or [],
                "confidence": c.confidence
            } for c in claims
        ],
        "created_at": session.created_at
    }


@router.get("/{session_id}/sources", response_model=List[SourceSchema])
def get_sources(session_id: str, db: Session = Depends(get_db)):
    sources = db.query(Source).filter(Source.session_id == session_id).all()
    return sources


@router.get("/{session_id}/status", response_model=SessionStatusResponse)
def get_status(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found.")

    sources_count = db.query(Source).filter(Source.session_id == session_id).count()
    claims_count = db.query(VerifiedClaim).filter(VerifiedClaim.session_id == session_id).count()
    verified_claims_count = db.query(VerifiedClaim).filter(
        VerifiedClaim.session_id == session_id,
        VerifiedClaim.status.in_(["Supported", "Partially Supported"])
    ).count()

    # Calculate individual agent status states for UI
    p = session.progress_percent
    
    def get_agent_state(min_p, max_p, current_agent_name, agent_key):
        if session.status == "completed":
            return "completed"
        if session.status == "failed":
            return "failed"
        if p >= max_p:
            return "completed"
        if p >= min_p:
            return "running"
        return "waiting"

    agents_info = [
        {
            "name": "Research Planner",
            "status": get_agent_state(0, 25, session.current_agent, "planner"),
            "activity": "Decomposing research query into structured sub-topics",
            "progress": min(100, int((p / 25) * 100)) if p <= 25 else 100
        },
        {
            "name": "Research Agents",
            "status": get_agent_state(25, 60, session.current_agent, "researcher"),
            "activity": "Investigating sub-topics via web search & FAISS RAG store",
            "progress": min(100, max(0, int(((p - 25) / 35) * 100))) if 25 < p <= 60 else (100 if p > 60 else 0)
        },
        {
            "name": "Fact Checker",
            "status": get_agent_state(60, 78, session.current_agent, "fact_checker"),
            "activity": "Verifying claims & cross-referencing supporting evidence",
            "progress": min(100, max(0, int(((p - 60) / 18) * 100))) if 60 < p <= 78 else (100 if p > 78 else 0)
        },
        {
            "name": "Analyst",
            "status": get_agent_state(78, 90, session.current_agent, "analyst"),
            "activity": "Synthesizing trends, structural relationships & trade-offs",
            "progress": min(100, max(0, int(((p - 78) / 12) * 100))) if 78 < p <= 90 else (100 if p > 90 else 0)
        },
        {
            "name": "Critic",
            "status": get_agent_state(90, 96, session.current_agent, "critic"),
            "activity": "Auditing completeness & evaluating academic peer review score",
            "progress": min(100, max(0, int(((p - 90) / 6) * 100))) if 90 < p <= 96 else (100 if p > 96 else 0)
        },
        {
            "name": "Report Writer",
            "status": get_agent_state(96, 100, session.current_agent, "writer"),
            "activity": "Compiling 13-section structured Markdown research report",
            "progress": min(100, max(0, int(((p - 96) / 4) * 100))) if 96 < p <= 100 else (100 if p > 100 else 0)
        }
    ]

    return {
        "id": session.id,
        "query": session.query,
        "status": session.status,
        "current_agent": session.current_agent,
        "progress_percent": session.progress_percent,
        "iterations": session.iterations or 1,
        "agents": [AgentStatusSchema.model_validate(a) for a in agents_info],
        "sources_count": sources_count,
        "claims_count": claims_count,
        "verified_claims_count": verified_claims_count,
        "report_markdown": session.report_markdown,
        "error_message": session.error_message
    }


@router.get("/{session_id}/stream")
async def stream_session_status(session_id: str):
    """
    SSE Stream for live real-time agent updates
    """
    queue = asyncio.Queue()
    if session_id not in sse_queues:
        sse_queues[session_id] = []
    sse_queues[session_id].append(queue)

    async def event_generator():
        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") in ["completed", "failed"]:
                    break
        except asyncio.CancelledError:
            pass
        finally:
            if session_id in sse_queues and queue in sse_queues[session_id]:
                sse_queues[session_id].remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
