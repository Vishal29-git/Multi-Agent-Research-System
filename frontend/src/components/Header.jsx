import React from 'react';
import { Sparkles, ShieldCheck } from 'lucide-react';

export default function Header({ isRunning }) {
  return (
    <header className="header">
      <div className="header-title">
        <Sparkles size={24} style={{ color: '#2563eb' }} />
        <div>
          <span>🔬 AI Research Lab</span>
          <div className="header-subtitle">Multi-Agent Research Platform</div>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: '#059669', backgroundColor: '#ecfdf5', padding: '0.35rem 0.75rem', borderRadius: '20px', border: '1px solid #a7f3d0' }}>
          <ShieldCheck size={14} />
          <span>100% Free & Local</span>
        </div>
      </div>
    </header>
  );
}
