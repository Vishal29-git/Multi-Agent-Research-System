import React from 'react';
import { 
  Compass, Search, ShieldCheck, BarChart3, CheckSquare, 
  FileText, Loader2, CheckCircle2, AlertCircle, Clock 
} from 'lucide-react';

const AGENT_ICONS = {
  "Research Planner": Compass,
  "Research Agents": Search,
  "Fact Checker": ShieldCheck,
  "Analyst": BarChart3,
  "Critic": CheckSquare,
  "Report Writer": FileText,
};

export default function AgentStatusView({ statusData }) {
  if (!statusData) return null;

  const {
    progress_percent = 0,
    sources_count = 0,
    claims_count = 0,
    verified_claims_count = 0,
    iterations = 1,
    agents = [],
    query,
    status
  } = statusData;

  const renderBadge = (agentStatus) => {
    switch (agentStatus) {
      case 'running':
        return (
          <span className="badge badge-running">
            <Loader2 size={12} className="animate-spin" /> Running
          </span>
        );
      case 'completed':
        return (
          <span className="badge badge-completed">
            <CheckCircle2 size={12} /> Completed
          </span>
        );
      case 'failed':
        return (
          <span className="badge badge-failed">
            <AlertCircle size={12} /> Failed
          </span>
        );
      default:
        return (
          <span className="badge badge-waiting">
            <Clock size={12} /> Waiting
          </span>
        );
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f9fafb' }}>
            Research Progress
          </h2>
          <div style={{ fontSize: '0.85rem', color: '#9ca3af', marginTop: '0.2rem' }}>
            Query: "{query}"
          </div>
        </div>
        <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#3b82f6' }}>
          {progress_percent}%
        </div>
      </div>

      {/* Progress Bar */}
      <div className="progress-bar-container" style={{ marginBottom: '1.5rem' }}>
        <div
          className="progress-bar-fill"
          style={{ width: `${progress_percent}%` }}
        />
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-box">
          <div className="stat-value">{sources_count}</div>
          <div className="stat-label">Sources Found</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{claims_count}</div>
          <div className="stat-label">Claims Identified</div>
        </div>
        <div className="stat-box">
          <div className="stat-value" style={{ color: '#10b981' }}>{verified_claims_count}</div>
          <div className="stat-label">Claims Verified</div>
        </div>
        <div className="stat-box">
          <div className="stat-value" style={{ color: '#8b5cf6' }}>{iterations}</div>
          <div className="stat-label">Research Iterations</div>
        </div>
      </div>

      <h3 style={{ fontSize: '1rem', fontWeight: 600, marginTop: '1.5rem', marginBottom: '0.75rem', color: '#9ca3af' }}>
        Live Agent Workflow Status
      </h3>

      {/* Agents Grid */}
      <div className="agents-grid">
        {agents.map((agent, idx) => {
          const IconComponent = AGENT_ICONS[agent.name] || FileText;
          return (
            <div
              key={idx}
              className={`agent-card ${agent.status === 'running' ? 'running' : ''}`}
            >
              <div className="agent-card-header">
                <div className="agent-title">
                  <IconComponent size={18} className={agent.status === 'running' ? 'text-blue-400' : 'text-gray-400'} />
                  <span>{agent.name}</span>
                </div>
                {renderBadge(agent.status)}
              </div>
              <div className="agent-activity">
                {agent.activity}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
