import { useCallback, useEffect, useMemo, useState } from 'react';
import { FaExternalLinkAlt, FaFilter, FaRedo, FaSearch, FaSave, FaTimes, FaTrash } from 'react-icons/fa';
import { PriorityBadge, SourceBadge, StatusBadge } from '../components/Badge';
import { useNotification } from '../contexts/NotificationContext';
import { getOpportunities } from '../utils/api';
import '../styles/Dashboard.css';

const DEFAULT_FILTERS = {
  priority: [],
  source: [],
  minRelevance: 0,
  maxRelevance: 100,
  minDeadline: '',
  maxDeadline: '',
  analyzed: 'all',
  sortBy: 'scraped_at',
  sortOrder: 'desc',
};

export default function Dashboard() {
  const { error: notifyError, success: notifySuccess } = useNotification();
  const [opportunities, setOpportunities] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [presets, setPresets] = useState(() =>
    JSON.parse(localStorage.getItem('filterPresets') || '[]')
  );
  const [currentPreset, setCurrentPreset] = useState('');
  const [presetNameInput, setPresetNameInput] = useState('');
  const [showPresetInput, setShowPresetInput] = useState(false);

  useEffect(() => {
    getOpportunities()
      .then(setOpportunities)
      .catch(() => notifyError('Failed to load opportunities. Is the backend running?'))
      .finally(() => setLoading(false));
  }, []);

  const priorities = useMemo(() => [...new Set(opportunities.map(o => o.priority).filter(Boolean))], [opportunities]);
  const sources    = useMemo(() => [...new Set(opportunities.map(o => o.source_platform).filter(Boolean))], [opportunities]);

  const filtered = useMemo(() => {
    let result = opportunities;
    const q = searchQuery.trim().toLowerCase();
    if (q) result = result.filter(o =>
      o.title?.toLowerCase().includes(q) ||
      o.organization?.toLowerCase().includes(q) ||
      o.description?.toLowerCase().includes(q)
    );
    if (filters.priority.length) result = result.filter(o => filters.priority.includes(o.priority));
    if (filters.source.length)   result = result.filter(o => filters.source.includes(o.source_platform));
    result = result.filter(o => {
      const s = o.relevance_score || 0;
      return s >= filters.minRelevance && s <= filters.maxRelevance;
    });
    if (filters.minDeadline) result = result.filter(o => !o.deadline || new Date(o.deadline) >= new Date(filters.minDeadline));
    if (filters.maxDeadline) result = result.filter(o => !o.deadline || new Date(o.deadline) <= new Date(filters.maxDeadline));
    if (filters.analyzed === 'analyzed')   result = result.filter(o => o.processed_at);
    if (filters.analyzed === 'unanalyzed') result = result.filter(o => !o.processed_at);

    return [...result].sort((a, b) => {
      let cmp = 0;
      switch (filters.sortBy) {
        case 'deadline':    cmp = new Date(a.deadline || '9999') - new Date(b.deadline || '9999'); break;
        case 'relevance':   cmp = (b.relevance_score || 0) - (a.relevance_score || 0); break;
        case 'title':       cmp = (a.title || '').localeCompare(b.title || ''); break;
        case 'organization':cmp = (a.organization || '').localeCompare(b.organization || ''); break;
        case 'scraped_at':  cmp = new Date(b.scraped_at || 0) - new Date(a.scraped_at || 0); break;
        default: cmp = 0;
      }
      return filters.sortOrder === 'desc' ? -cmp : cmp;
    });
  }, [opportunities, searchQuery, filters]);

  const setFilter = useCallback((key, val) => setFilters(f => ({ ...f, [key]: val })), []);
  const toggleMulti = useCallback((key, val) =>
    setFilters(f => ({
      ...f,
      [key]: f[key].includes(val) ? f[key].filter(v => v !== val) : [...f[key], val],
    })), []);
  const resetFilters = () => { setFilters(DEFAULT_FILTERS); setSearchQuery(''); setCurrentPreset(''); };

  const savePreset = () => {
    const name = presetNameInput.trim();
    if (!name) return;
    const updated = [...presets.filter(p => p.name !== name), { id: Date.now(), name, filters, searchQuery }];
    localStorage.setItem('filterPresets', JSON.stringify(updated));
    setPresets(updated);
    setCurrentPreset(name);
    setPresetNameInput('');
    setShowPresetInput(false);
    notifySuccess(`Preset "${name}" saved`);
  };
  const loadPreset = (p) => { setFilters(p.filters); setSearchQuery(p.searchQuery); setCurrentPreset(p.name); };
  const deletePreset = (id) => {
    const updated = presets.filter(p => p.id !== id);
    localStorage.setItem('filterPresets', JSON.stringify(updated));
    setPresets(updated);
  };

  const activeCount =
    filters.priority.length + filters.source.length +
    (filters.minRelevance > 0 || filters.maxRelevance < 100 ? 1 : 0) +
    (filters.minDeadline || filters.maxDeadline ? 1 : 0) +
    (filters.analyzed !== 'all' ? 1 : 0) +
    (searchQuery.trim() ? 1 : 0);

  if (loading) return (
    <div className="dashboard">
      <div className="db-skeleton-grid">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="skeleton-card">
            <div className="skeleton" style={{ height: 20, width: '70%', marginBottom: 8 }} />
            <div className="skeleton" style={{ height: 14, width: '45%', marginBottom: 16 }} />
            <div className="skeleton" style={{ height: 12, width: '100%', marginBottom: 6 }} />
            <div className="skeleton" style={{ height: 12, width: '80%' }} />
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="dashboard">
      {/* Search + filter bar */}
      <div className="db-toolbar">
        <div className="db-search-wrap">
          <FaSearch className="db-search-icon" aria-hidden="true" />
          <input
            type="search"
            className="db-search form-control"
            placeholder="Search opportunities, organizations…"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            aria-label="Search opportunities"
          />
          {searchQuery && (
            <button className="db-search-clear icon-btn" onClick={() => setSearchQuery('')} aria-label="Clear search">
              <FaTimes />
            </button>
          )}
        </div>
        <button
          className={`btn btn-secondary btn-sm db-filter-toggle${activeCount ? ' db-filter-toggle--active' : ''}`}
          onClick={() => setShowFilters(v => !v)}
          aria-expanded={showFilters}
        >
          <FaFilter /> Filters {activeCount > 0 && <span className="db-badge">{activeCount}</span>}
        </button>
        {activeCount > 0 && (
          <button className="btn btn-ghost btn-sm" onClick={resetFilters}>
            <FaRedo /> Reset
          </button>
        )}
      </div>

      {/* Filters panel */}
      {showFilters && (
        <div className="db-filters">
          <div className="db-filters-grid">
            {/* Priority */}
            <div className="filter-section">
              <p className="filter-label">Priority</p>
              <div className="check-group">
                {priorities.map(p => (
                  <label key={p} className="check-label">
                    <input type="checkbox" checked={filters.priority.includes(p)} onChange={() => toggleMulti('priority', p)} />
                    <PriorityBadge priority={p} />
                  </label>
                ))}
                {!priorities.length && <span className="text-muted text-sm">No data yet</span>}
              </div>
            </div>

            {/* Source */}
            <div className="filter-section">
              <p className="filter-label">Source Platform</p>
              <div className="check-group">
                {sources.map(s => (
                  <label key={s} className="check-label">
                    <input type="checkbox" checked={filters.source.includes(s)} onChange={() => toggleMulti('source', s)} />
                    <SourceBadge source={s} />
                  </label>
                ))}
                {!sources.length && <span className="text-muted text-sm">No data yet</span>}
              </div>
            </div>

            {/* Relevance */}
            <div className="filter-section">
              <p className="filter-label">Relevance: {filters.minRelevance}% – {filters.maxRelevance}%</p>
              <div className="range-group">
                <input type="range" min={0} max={100} value={filters.minRelevance} onChange={e => setFilter('minRelevance', +e.target.value)} className="range-input" />
                <input type="range" min={0} max={100} value={filters.maxRelevance} onChange={e => setFilter('maxRelevance', +e.target.value)} className="range-input" />
              </div>
            </div>

            {/* Analysis */}
            <div className="filter-section">
              <p className="filter-label">Analysis Status</p>
              <select className="form-control" value={filters.analyzed} onChange={e => setFilter('analyzed', e.target.value)}>
                <option value="all">All</option>
                <option value="analyzed">Analyzed</option>
                <option value="unanalyzed">Not Analyzed</option>
              </select>
            </div>

            {/* Deadline */}
            <div className="filter-section">
              <p className="filter-label">Deadline Range</p>
              <div className="date-range">
                <input type="date" className="form-control" value={filters.minDeadline} onChange={e => setFilter('minDeadline', e.target.value)} />
                <span className="text-muted text-sm">to</span>
                <input type="date" className="form-control" value={filters.maxDeadline} onChange={e => setFilter('maxDeadline', e.target.value)} />
              </div>
            </div>

            {/* Sort */}
            <div className="filter-section">
              <p className="filter-label">Sort</p>
              <div className="sort-row">
                <select className="form-control" value={filters.sortBy} onChange={e => setFilter('sortBy', e.target.value)}>
                  <option value="scraped_at">Date Added</option>
                  <option value="deadline">Deadline</option>
                  <option value="relevance">Relevance</option>
                  <option value="title">Title</option>
                  <option value="organization">Organization</option>
                </select>
                <select className="form-control" value={filters.sortOrder} onChange={e => setFilter('sortOrder', e.target.value)}>
                  <option value="desc">Newest First</option>
                  <option value="asc">Oldest First</option>
                </select>
              </div>
            </div>
          </div>

          {/* Presets */}
          <div className="db-presets">
            <div className="db-presets-header">
              <span className="filter-label">Saved Presets</span>
              {!showPresetInput ? (
                <button className="btn btn-ghost btn-sm" onClick={() => setShowPresetInput(true)}>
                  <FaSave /> Save Current
                </button>
              ) : (
                <div className="preset-save-row">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Preset name…"
                    value={presetNameInput}
                    onChange={e => setPresetNameInput(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') savePreset(); if (e.key === 'Escape') setShowPresetInput(false); }}
                    autoFocus
                  />
                  <button className="btn btn-primary btn-sm" onClick={savePreset}>Save</button>
                  <button className="btn btn-ghost btn-sm" onClick={() => setShowPresetInput(false)}>Cancel</button>
                </div>
              )}
            </div>
            {presets.length > 0 && (
              <div className="preset-chips">
                {presets.map(p => (
                  <div key={p.id} className={`preset-chip${currentPreset === p.name ? ' preset-chip--active' : ''}`}>
                    <button onClick={() => loadPreset(p)}>{p.name}</button>
                    <button onClick={() => deletePreset(p.id)} aria-label={`Delete preset ${p.name}`}><FaTrash /></button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Results header */}
      <div className="db-results-header">
        <span className="db-count">
          <strong>{filtered.length}</strong> {filtered.length === 1 ? 'opportunity' : 'opportunities'}
          {filtered.length !== opportunities.length && ` of ${opportunities.length}`}
        </span>
        {currentPreset && <span className="db-preset-tag">Filter: {currentPreset}</span>}
      </div>

      {/* Grid */}
      {filtered.length > 0 ? (
        <div className="db-grid">
          {filtered.map(opp => <OpportunityCard key={opp.id} opp={opp} />)}
        </div>
      ) : (
        <div className="empty-state">
          <FaSearch />
          <p><strong>No opportunities found</strong></p>
          <p>Try adjusting your filters or scrape new opportunities.</p>
          {activeCount > 0 && <button className="btn btn-secondary btn-sm" onClick={resetFilters}>Clear Filters</button>}
        </div>
      )}
    </div>
  );
}

function OpportunityCard({ opp }) {
  const daysLeft = opp.deadline
    ? Math.ceil((new Date(opp.deadline) - Date.now()) / 86_400_000)
    : null;

  const deadlineClass =
    daysLeft === null ? '' :
    daysLeft < 0  ? 'deadline--past' :
    daysLeft < 7  ? 'deadline--urgent' :
    daysLeft < 14 ? 'deadline--soon' : '';

  return (
    <article className="opp-card">
      <div className="opp-card-header">
        <PriorityBadge priority={opp.priority || 'Low'} />
        {opp.processed_at && <StatusBadge status="analyzed" />}
      </div>

      <h3 className="opp-title" title={opp.title}>{opp.title || 'Untitled'}</h3>

      <div className="opp-meta">
        <span className="opp-org">{opp.organization || 'Unknown org'}</span>
        <SourceBadge source={opp.source_platform} />
      </div>

      {opp.deadline && (
        <div className={`opp-deadline ${deadlineClass}`}>
          <span>
            Deadline: {new Date(opp.deadline).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
          </span>
          {daysLeft !== null && daysLeft >= 0 && (
            <span className="deadline-badge">{daysLeft}d left</span>
          )}
          {daysLeft !== null && daysLeft < 0 && (
            <span className="deadline-badge deadline-badge--past">Expired</span>
          )}
        </div>
      )}

      {opp.processed_at && (
        <div className="opp-scores">
          <ScoreBar label="Relevance" value={opp.relevance_score} color="var(--accent)" />
          <ScoreBar label="Confidence" value={opp.confidence_score} color="var(--success)" />
        </div>
      )}

      {opp.ai_summary && (
        <p className="opp-summary">{opp.ai_summary}</p>
      )}

      <div className="opp-card-footer">
        {opp.url ? (
          <a href={opp.url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-sm">
            View Opportunity <FaExternalLinkAlt />
          </a>
        ) : (
          <span className="text-muted text-sm">No link available</span>
        )}
      </div>
    </article>
  );
}

function ScoreBar({ label, value = 0, color }) {
  return (
    <div className="score-row">
      <span className="score-row-label">{label}</span>
      <div className="score-bar">
        <div className="score-fill" style={{ width: `${value}%`, background: color }} />
      </div>
      <span className="score-row-val">{value}%</span>
    </div>
  );
}
