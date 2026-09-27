import React from 'react';
import { PlusCircle, History, FileText, CheckCircle2, Clock, AlertCircle } from 'lucide-react';

export default function Sidebar({ sessions, activeSessionId, onSelectSession, onNewResearch }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
          <History size={18} />
          <span>Research History</span>
        </div>
      </div>
      <div style={{ padding: '0 1rem' }}>
        <button className="btn-new-research" onClick={onNewResearch}>
          <PlusCircle size={16} />
          <span>New Research Query</span>
        </button>
      </div>
      <div className="history-list">
        {sessions.length === 0 ? (
          <div style={{ padding: '1.5rem', textAlign: 'center', color: '#6b7280', fontSize: '0.85rem' }}>
            No research history yet. Start your first query!
          </div>
        ) : (
          sessions.map((session) => {
            const isActive = session.id === activeSessionId;
            return (
              <div
                key={session.id}
                className={`history-item ${isActive ? 'active' : ''}`}
                onClick={() => onSelectSession(session.id)}
              >
                <div className="history-item-title" title={session.query}>
                  {session.query}
                </div>
                <div className="history-item-meta">
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    {session.status === 'completed' && <CheckCircle2 size={12} style={{ color: '#10b981' }} />}
                    {session.status === 'running' && <Clock size={12} style={{ color: '#3b82f6' }} />}
                    {session.status === 'failed' && <AlertCircle size={12} style={{ color: '#ef4444' }} />}
                    <span style={{ textTransform: 'capitalize' }}>{session.status}</span>
                  </span>
                  <span>{new Date(session.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}
