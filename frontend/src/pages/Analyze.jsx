import { useEffect, useState } from 'react';
import { FaCheckCircle, FaRobot, FaSpinner, FaTimesCircle } from 'react-icons/fa';
import { PriorityBadge, SourceBadge } from '../components/Badge';
import { useNotification } from '../contexts/NotificationContext';
import { analyzeAll, analyzeBySource, analyzeSingle, getAiStatus, getOpportunities } from '../utils/api';
import '../styles/Analyze.css';

const SOURCES = ['Devex','Impactpool','UNDP','World Bank','DevelopmentAid'];

export default function Analyze() {
  const { success, error: notifyError, info } = useNotification();
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [aiStatus, setAiStatus] = useState(null);
  const [tab, setTab] = useState('unanalyzed');
  const [selectedSource, setSelectedSource] = useState('');
  const [analyzingId, setAnalyzingId] = useState(null);

  useEffect(() => {
    loadAll();
    getAiStatus().then(setAiStatus).catch(() => {});
  }, []);

  const loadAll = () =>
    getOpportunities().then(setOpportunities).catch(() => {});

  const handleAnalyzeAll = async () => {
    setLoading(true);
    try {
      const data = await analyzeAll();
      success(`Analyzed ${data.total_analyzed} opportunities`);
      await loadAll();
    } catch (e) { notifyError(e.message); }
    finally { setLoading(false); }
  };

  const handleAnalyzeBySource = async () => {
    if (!selectedSource) { info('Select a source first'); return; }
    setLoading(true);
    try {
      const data = await analyzeBySource(selectedSource);
      success(`Analyzed ${data.total_analyzed} from ${selectedSource}`);
      await loadAll();
    } catch (e) { notifyError(e.message); }
    finally { setLoading(false); }
  };

  const handleSingle = async (id) => {
    setAnalyzingId(id);
    try {
      await analyzeSingle(id);
      success('Analysis complete');
      await loadAll();
    } catch (e) { notifyError(e.message); }
    finally { setAnalyzingId(null); }
  };

  const shown = opportunities.filter(o =>
    tab === 'analyzed' ? !!o.processed_at : !o.processed_at
  );
  const analyzed   = opportunities.filter(o => o.processed_at).length;
  const unanalyzed = opportunities.length - analyzed;

  const relevColor = (s) => s >= 75 ? 'var(--success)' : s >= 50 ? 'var(--warning)' : 'var(--danger)';

  return (
    <div className="analyze-page">
      <div className="page-header">
        <h1 className="page-title"><FaRobot /> AI Analysis</h1>
        <p className="page-subtitle">Score and summarize opportunities using OpenAI</p>
      </div>

      {/* AI Status banner */}
      {aiStatus && (
        <div className={`ai-banner${aiStatus.available ? ' ai-banner--ok' : ' ai-banner--off'}`}>
          {aiStatus.available
            ? <><FaCheckCircle /> AI active &mdash; {aiStatus.model || 'GPT-3.5-turbo'}</>
            : <><FaTimesCircle /> AI disabled &mdash; set <code>OPENAI_API_KEY</code> to enable</>}
        </div>
      )}

      {/* Controls */}
      {aiStatus?.available && (
        <div className="analyze-controls">
          <button className="btn btn-primary" onClick={handleAnalyzeAll} disabled={loading || unanalyzed === 0}>
            {loading ? <><FaSpinner className="spin" /> Analyzing…</> : `Analyze All Unanalyzed (${unanalyzed})`}
          </button>
          <div className="analyze-source-group">
            <select className="form-control" value={selectedSource} onChange={e => setSelectedSource(e.target.value)} disabled={loading}>
              <option value="">Select source…</option>
              {SOURCES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <button className="btn btn-secondary" onClick={handleAnalyzeBySource} disabled={loading || !selectedSource}>
              Analyze Source
            </button>
          </div>
        </div>
      )}

      {/* Tab filter */}
      <div className="analyze-tabs">
        <button className={`tab${tab === 'unanalyzed' ? ' tab--active' : ''}`} onClick={() => setTab('unanalyzed')}>
          Unanalyzed <span className="tab-count">{unanalyzed}</span>
        </button>
        <button className={`tab${tab === 'analyzed' ? ' tab--active' : ''}`} onClick={() => setTab('analyzed')}>
          Analyzed <span className="tab-count">{analyzed}</span>
        </button>
      </div>

      {/* List */}
      {shown.length === 0 ? (
        <div className="empty-state">
          <FaRobot />
          <p>{tab === 'analyzed' ? 'No analyzed opportunities yet' : 'All opportunities have been analyzed!'}</p>
        </div>
      ) : (
        <div className="analyze-list">
          {shown.map(opp => (
            <div key={opp.id} className="analyze-card">
              <div className="analyze-card-top">
                <div className="analyze-card-meta">
                  <SourceBadge source={opp.source_platform} />
                  <PriorityBadge priority={opp.priority || 'Low'} />
                </div>
                {!opp.processed_at && (
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleSingle(opp.id)}
                    disabled={!!analyzingId}
                  >
                    {analyzingId === opp.id ? <><FaSpinner className="spin" /> Analyzing…</> : 'Analyze'}
                  </button>
                )}
              </div>

              <h3 className="analyze-title">{opp.title}</h3>
              <p className="analyze-org">{opp.organization}</p>

              {opp.processed_at && (
                <>
                  <div className="analyze-scores">
                    <AnalyzeBar label="Relevance" value={opp.relevance_score} color={relevColor(opp.relevance_score)} />
                    <AnalyzeBar label="Confidence" value={opp.confidence_score} color="var(--info)" />
                  </div>
                  {opp.ai_summary && <p className="analyze-summary">{opp.ai_summary}</p>}
                  <p className="analyze-date text-muted text-xs">
                    Analyzed {new Date(opp.processed_at).toLocaleDateString()}
                  </p>
                </>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Info */}
      <div className="info-section">
        <h3>How AI Analysis Works</h3>
        <ul className="info-list">
          <li><strong>Relevance Score:</strong> 0–100 match against Africa digital focus criteria</li>
          <li><strong>Confidence Score:</strong> How well-described the opportunity is</li>
          <li><strong>Priority:</strong> High / Medium / Low action recommendation</li>
          <li><strong>AI Summary:</strong> Concise description of key details</li>
        </ul>
      </div>
    </div>
  );
}

function AnalyzeBar({ label, value = 0, color }) {
  return (
    <div className="a-bar-row">
      <span className="a-bar-label">{label}</span>
      <div className="a-bar-track">
        <div className="a-bar-fill" style={{ width: `${value}%`, background: color }} />
      </div>
      <span className="a-bar-val">{value}%</span>
    </div>
  );
}
