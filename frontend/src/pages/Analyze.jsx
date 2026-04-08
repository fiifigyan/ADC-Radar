import React, { useState, useEffect } from 'react';
import '../styles/Analyze.css';

const Analyze = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aiStatus, setAiStatus] = useState(null);
  const [filterAnalyzed, setFilterAnalyzed] = useState('unanalyzed');
  const [selectedSource, setSelectedSource] = useState('');

  const sources = [
    'Devex',
    'Impactpool',
    'UNDP',
    'World Bank',
    'DevelopmentAid',
  ];

  useEffect(() => {
    loadOpportunities();
    loadAiStatus();
  }, []);

  const loadOpportunities = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/opportunities');
      if (response.ok) {
        const data = await response.json();
        setOpportunities(data);
      }
    } catch (err) {
      console.error('Error loading opportunities:', err);
    }
  };

  const loadAiStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/ai/status');
      if (response.ok) {
        const data = await response.json();
        setAiStatus(data);
      }
    } catch (err) {
      console.error('Error loading AI status:', err);
    }
  };

  const analyzeAll = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/analyze/batch/all', {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        alert(`✓ Analyzed ${data.total_analyzed} opportunities!`);
        await loadOpportunities();
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to analyze opportunities');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const analyzeBySource = async () => {
    if (!selectedSource) {
      alert('Please select a source');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/analyze/batch/by-source', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: selectedSource }),
      });

      if (response.ok) {
        const data = await response.json();
        alert(`✓ Analyzed ${data.total_analyzed} opportunities from ${selectedSource}!`);
        await loadOpportunities();
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to analyze opportunities');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const analyzeSingle = async (opportunityId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:5000/api/analyze/${opportunityId}`, {
        method: 'POST',
      });

      if (response.ok) {
        alert('✓ Opportunity analyzed!');
        await loadOpportunities();
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to analyze opportunity');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Filter opportunities
  const filteredOpportunities = opportunities.filter((opp) => {
    if (filterAnalyzed === 'analyzed') {
      return opp.processed_at !== null;
    } else {
      return opp.processed_at === null;
    }
  });

  const getRelevanceColor = (score) => {
    if (score >= 75) return '#2ecc71'; // Green
    if (score >= 50) return '#f39c12'; // Orange
    return '#e74c3c'; // Red
  };

  const getPriorityBadgeColor = (priority) => {
    switch (priority) {
      case 'High': return '#e74c3c';
      case 'Medium': return '#f39c12';
      case 'Low': return '#95a5a6';
      default: return '#34495e';
    }
  };

  return (
    <div className="analyze-page">
      <h1>🤖 AI Analysis</h1>
      <p className="subtitle">Analyze opportunities with AI for relevance and insights</p>

      {error && <div className="error-message">❌ {error}</div>}

      {/* AI Status Section */}
      {aiStatus && (
        <div className={`ai-status ${aiStatus.available ? 'available' : 'unavailable'}`}>
          <h3>
            {aiStatus.available ? '✓' : '✕'} AI Status
          </h3>
          <p>{aiStatus.message}</p>
          {!aiStatus.available && (
            <p className="warning">
              OpenAI API key not configured. Set OPENAI_API_KEY environment variable to enable AI analysis.
            </p>
          )}
        </div>
      )}

      {/* Analysis Controls */}
      {aiStatus?.available && (
        <div className="analysis-controls">
          <div className="control-group">
            <button
              className="btn btn-primary"
              onClick={analyzeAll}
              disabled={loading || filteredOpportunities.length === 0}
            >
              {loading ? '⏳ Analyzing...' : '🚀 Analyze All Unanalyzed'}
            </button>
          </div>

          <div className="control-group">
            <select
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
              disabled={loading}
            >
              <option value="">Select source to analyze...</option>
              {sources.map((source) => (
                <option key={source} value={source}>
                  {source}
                </option>
              ))}
            </select>
            <button
              className="btn btn-secondary"
              onClick={analyzeBySource}
              disabled={loading || !selectedSource}
            >
              {loading ? '⏳ Analyzing...' : '📥 Analyze Source'}
            </button>
          </div>
        </div>
      )}

      {/* Filter Controls */}
      <div className="filter-controls">
        <label>
          <input
            type="radio"
            value="unanalyzed"
            checked={filterAnalyzed === 'unanalyzed'}
            onChange={(e) => setFilterAnalyzed(e.target.value)}
          />
          Unanalyzed ({opportunities.filter((o) => !o.processed_at).length})
        </label>
        <label>
          <input
            type="radio"
            value="analyzed"
            checked={filterAnalyzed === 'analyzed'}
            onChange={(e) => setFilterAnalyzed(e.target.value)}
          />
          Analyzed ({opportunities.filter((o) => o.processed_at).length})
        </label>
      </div>

      {/* Opportunities List */}
      <div className="opportunities-grid">
        {filteredOpportunities.length === 0 ? (
          <div className="empty-state">
            <p>
              {filterAnalyzed === 'analyzed'
                ? 'No analyzed opportunities yet'
                : 'All opportunities have been analyzed!'}
            </p>
          </div>
        ) : (
          filteredOpportunities.map((opp) => (
            <div key={opp.id} className="opportunity-card">
              <div className="card-header">
                <h3>{opp.title}</h3>
                <span className="source-badge">{opp.source_platform}</span>
              </div>

              <div className="card-org">
                <strong>{opp.organization}</strong>
              </div>

              {opp.processed_at ? (
                <>
                  <div className="score-section">
                    <div className="score-item">
                      <label>Relevance</label>
                      <div className="score-bar">
                        <div
                          className="score-fill"
                          style={{
                            width: `${opp.relevance_score}%`,
                            backgroundColor: getRelevanceColor(opp.relevance_score),
                          }}
                        >
                          {opp.relevance_score}%
                        </div>
                      </div>
                    </div>

                    <div className="score-item">
                      <label>Confidence</label>
                      <div className="score-bar">
                        <div
                          className="score-fill"
                          style={{
                            width: `${opp.confidence_score}%`,
                            backgroundColor: '#3498db',
                          }}
                        >
                          {opp.confidence_score}%
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="priority-section">
                    <span
                      className="priority-badge"
                      style={{ backgroundColor: getPriorityBadgeColor(opp.priority) }}
                    >
                      {opp.priority}
                    </span>
                  </div>

                  {opp.ai_summary && (
                    <div className="summary-section">
                      <h4>AI Summary</h4>
                      <p>{opp.ai_summary}</p>
                    </div>
                  )}

                  <div className="metadata">
                    <small>
                      Analyzed: {new Date(opp.processed_at).toLocaleDateString()}
                    </small>
                  </div>
                </>
              ) : (
                <div className="unanalyzed-section">
                  <p className="unanalyzed-text">Not yet analyzed</p>
                  <button
                    className="btn btn-small btn-analyze"
                    onClick={() => analyzeSingle(opp.id)}
                    disabled={loading}
                  >
                    {loading ? '⏳' : '🔍'} Analyze
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <div className="info-box">
        <h3>ℹ️ How AI Analysis Works</h3>
        <ul>
          <li>
            <strong>Relevance Score:</strong> How well the opportunity matches Africa development focus
            (0-100 scale)
          </li>
          <li>
            <strong>Confidence Score:</strong> How reliable the AI assessment is based on available
            information
          </li>
          <li>
            <strong>Priority:</strong> Recommended action level (High/Medium/Low)
          </li>
          <li>
            <strong>AI Summary:</strong> Concise overview of key opportunity details
          </li>
          <li>Use batch analysis to analyze multiple opportunities at once</li>
          <li>Individual analysis available for each unanalyzed opportunity</li>
        </ul>
      </div>
    </div>
  );
};

export default Analyze;
