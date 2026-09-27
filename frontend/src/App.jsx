import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ResearchForm from './components/ResearchForm';
import AgentStatusView from './components/AgentStatusView';
import ReportViewer from './components/ReportViewer';
import { startResearch, listSessions, getSessionDetail, getSessionStatus, subscribeStatusSSE } from './services/api';
import { AlertCircle } from 'lucide-react';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [sessionDetail, setSessionDetail] = useState(null);
  const [statusData, setStatusData] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  // Fetch session history list on load
  const loadSessions = async () => {
    try {
      const data = await listSessions();
      setSessions(data);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  // Fetch detail & status when activeSessionId changes
  useEffect(() => {
    if (!activeSessionId) {
      setSessionDetail(null);
      setStatusData(null);
      return;
    }

    let isMounted = true;
    let pollInterval = null;
    let unsubscribeSSE = null;

    const fetchStatusAndDetail = async () => {
      try {
        const statusRes = await getSessionStatus(activeSessionId);
        if (isMounted) setStatusData(statusRes);

        if (statusRes.status === 'completed' || statusRes.status === 'failed') {
          const detailRes = await getSessionDetail(activeSessionId);
          if (isMounted) setSessionDetail(detailRes);
        }
      } catch (err) {
        console.error('Error fetching session info:', err);
      }
    };

    fetchStatusAndDetail();

    // Subscribe to SSE stream for active sessions
    unsubscribeSSE = subscribeStatusSSE(
      activeSessionId,
      async (sseData) => {
        if (!isMounted) return;
        // Refresh full status payload
        const updatedStatus = await getSessionStatus(activeSessionId);
        setStatusData(updatedStatus);

        if (updatedStatus.status === 'completed') {
          const updatedDetail = await getSessionDetail(activeSessionId);
          setSessionDetail(updatedDetail);
          loadSessions();
        }
      },
      (err) => {
        // Fallback to polling if SSE encounters network glitch
        if (!pollInterval) {
          pollInterval = setInterval(fetchStatusAndDetail, 2000);
        }
      }
    );

    // Backup interval polling for robust UI updates
    pollInterval = setInterval(fetchStatusAndDetail, 2500);

    return () => {
      isMounted = false;
      if (pollInterval) clearInterval(pollInterval);
      if (unsubscribeSSE) unsubscribeSSE();
    };
  }, [activeSessionId]);

  const handleStartResearch = async (queryText) => {
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const newSession = await startResearch(queryText);
      await loadSessions();
      setActiveSessionId(newSession.id);
    } catch (err) {
      setErrorMessage(err.response?.data?.detail || 'Failed to start research session.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSelectSession = (id) => {
    setActiveSessionId(id);
    setErrorMessage(null);
  };

  const handleNewResearch = () => {
    setActiveSessionId(null);
    setSessionDetail(null);
    setStatusData(null);
    setErrorMessage(null);
  };

  return (
    <div className="app-layout">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewResearch={handleNewResearch}
      />

      <div className="main-content">
        <Header isRunning={statusData?.status === 'running'} />

        <main className="content-body">
          {errorMessage && (
            <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#f87171', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={18} />
              <span>{errorMessage}</span>
            </div>
          )}

          {!activeSessionId && (
            <ResearchForm
              onSubmit={handleStartResearch}
              isSubmitting={isSubmitting}
            />
          )}

          {activeSessionId && (
            <>
              {statusData && <AgentStatusView statusData={statusData} />}

              {sessionDetail && sessionDetail.report_markdown && (
                <ReportViewer sessionData={sessionDetail} />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
