import React from 'react';
import { ExternalLink, Link2 } from 'lucide-react';

export default function SourcesTab({ sources = [] }) {
  if (sources.length === 0) {
    return <p style={{ color: '#64748b' }}>No source documents indexed for this research session.</p>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {sources.map((src, idx) => (
        <div
          key={idx}
          style={{
            backgroundColor: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            padding: '1rem'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
            <a
              href={src.url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                fontWeight: 600,
                color: '#2563eb',
                fontSize: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                textDecoration: 'none'
              }}
            >
              <Link2 size={16} />
              <span>{src.title}</span>
              <ExternalLink size={14} />
            </a>
            <span style={{ fontSize: '0.75rem', color: '#475569', backgroundColor: '#e2e8f0', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
              Relevance: {(src.relevance_score || 1.0).toFixed(2)}
            </span>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#334155', lineHeight: 1.5 }}>
            {src.snippet || 'Indexed search snippet available in FAISS RAG Store.'}
          </p>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.4rem', wordBreak: 'break-all' }}>
            {src.url}
          </div>
        </div>
      ))}
    </div>
  );
}
