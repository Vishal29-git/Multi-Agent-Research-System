import React, { useState } from 'react';
import { Search, Sparkles, ArrowRight } from 'lucide-react';

const SUGGESTIONS = [
  "How could AGI emerge in the future?",
  "Impact of GenAI on software development",
  "Future of autonomous AI agents",
  "AI in healthcare & clinical diagnostics"
];

export default function ResearchForm({ onSubmit, isSubmitting }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !isSubmitting) {
      onSubmit(query.trim());
    }
  };

  const handleSuggestion = (text) => {
    setQuery(text);
  };

  return (
    <div className="hero-section">
      <h1 className="hero-title">Autonomous Multi-Agent AI Research</h1>
      <p className="hero-subtitle">
        Enter your research prompt below. Specialized AI agents (Planner, Researcher, Fact Checker, Analyst, Critic, Writer) will collaborate to search, verify evidence, analyze trends, and compile a structured report.
      </p>

      <form onSubmit={handleSubmit} className="search-box-container">
        <textarea
          className="search-textarea"
          placeholder="What would you like to research? (e.g. How could AGI emerge in the future?)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
          disabled={isSubmitting}
        />
        <div className="search-actions">
          <button
            type="submit"
            className="btn-start-research"
            disabled={!query.trim() || isSubmitting}
          >
            {isSubmitting ? (
              <span>Initializing Workflow...</span>
            ) : (
              <>
                <Sparkles size={18} />
                <span>Start Research</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </div>
      </form>

      <div className="suggestions-container">
        {SUGGESTIONS.map((text, idx) => (
          <button
            key={idx}
            type="button"
            className="suggestion-pill"
            onClick={() => handleSuggestion(text)}
          >
            {text}
          </button>
        ))}
      </div>
    </div>
  );
}
