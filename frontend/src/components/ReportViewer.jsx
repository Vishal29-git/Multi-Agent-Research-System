import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Download, Check, ShieldCheck } from 'lucide-react';
import SourcesTab from './SourcesTab';

export default function ReportViewer({ sessionData }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [copied, setCopied] = useState(false);

  if (!sessionData || !sessionData.report_markdown) return null;

  const { report_markdown, sources = [], claims = [], query } = sessionData;

  const handleCopy = () => {
    navigator.clipboard.writeText(report_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([report_markdown], { type: 'text/markdown' });
    element.href = URL.createObjectURL(file);
    element.download = `Research_Report_${query.substring(0, 30).replace(/\s+/g, '_')}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#059669', fontSize: '0.85rem', fontWeight: 600 }}>
            <ShieldCheck size={16} />
            <span>Verified Peer-Reviewed Multi-Agent Output</span>
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, marginTop: '0.2rem', color: '#0f172a' }}>
            Final Research Report
          </h2>
        </div>

        <div className="report-actions">
          <button className="btn-secondary" onClick={handleCopy}>
            {copied ? <Check size={14} style={{ color: '#059669' }} /> : <Copy size={14} />}
            <span>{copied ? 'Copied!' : 'Copy Report'}</span>
          </button>
          <button className="btn-secondary" onClick={handleDownload}>
            <Download size={14} />
            <span>Download .MD</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-header">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview & Full Report
        </button>
        <button
          className={`tab-btn ${activeTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('evidence')}
        >
          Verified Evidence Matrix ({claims.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'sources' ? 'active' : ''}`}
          onClick={() => setActiveTab('sources')}
        >
          Sources & Citations ({sources.length})
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="markdown-body">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {report_markdown}
          </ReactMarkdown>
        </div>
      )}

      {activeTab === 'evidence' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {claims.length === 0 ? (
            <p style={{ color: '#64748b' }}>No claim verification records available.</p>
          ) : (
            claims.map((item, idx) => (
              <div
                key={idx}
                style={{
                  backgroundColor: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  padding: '1rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      padding: '0.2rem 0.6rem',
                      borderRadius: '12px',
                      textTransform: 'uppercase',
                      backgroundColor: item.status === 'Supported' ? '#ecfdf5' : '#fffbeb',
                      color: item.status === 'Supported' ? '#047857' : '#b45309',
                      border: `1px solid ${item.status === 'Supported' ? '#a7f3d0' : '#fde68a'}`
                    }}
                  >
                    {item.status}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                    Confidence: <strong style={{ color: '#334155' }}>{item.confidence}</strong>
                  </span>
                </div>
                <div style={{ fontWeight: 600, fontSize: '0.95rem', color: '#0f172a', marginBottom: '0.4rem' }}>
                  "{item.claim}"
                </div>
                {item.evidence && item.evidence.length > 0 && (
                  <div style={{ fontSize: '0.85rem', color: '#334155', backgroundColor: '#ffffff', border: '1px solid #e2e8f0', padding: '0.6rem', borderRadius: '6px', marginTop: '0.4rem' }}>
                    <strong style={{ color: '#0f172a' }}>Evidence:</strong>
                    <ul style={{ paddingLeft: '1.2rem', marginTop: '0.2rem' }}>
                      {item.evidence.map((ev, i) => (
                        <li key={i}>{ev}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'sources' && (
        <SourcesTab sources={sources} />
      )}
    </div>
  );
}
