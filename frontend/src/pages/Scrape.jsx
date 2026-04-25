import { useEffect, useState } from 'react';
import { FaCheck, FaDownload, FaSpinner, FaSyncAlt, FaTimes, FaTrash } from 'react-icons/fa';
import { useNotification } from '../contexts/NotificationContext';
import { createSchedule, deleteSchedule, getScrapeStats, getSchedules, scrapeAll, scrapeSource, syncNotion, updateSchedule } from '../utils/api';
import '../styles/Scrape.css';

const SOURCES = [
  { value: 'Devex',          color: '#EC4899' },
  { value: 'Impactpool',     color: '#6366F1' },
  { value: 'UNDP',           color: '#06B6D4' },
  { value: 'World Bank',     color: '#3B82F6' },
  { value: 'DevelopmentAid', color: '#8B5CF6' },
];

const EMPTY_SCHEDULE = { name: '', type: 'daily', time: '10:00', day_of_week: 0, interval_hours: 24, sources: [], enabled: true };

export default function Scrape() {
  const { success, error: notifyError, info } = useNotification();
  const [loading, setLoading]   = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [selected, setSelected] = useState(SOURCES.map(s => s.value));
  const [results, setResults]   = useState(null);
  const [stats, setStats]       = useState(null);
  const [schedules, setSchedules] = useState({});
  const [showForm, setShowForm] = useState(false);
  const [form, setForm]         = useState(EMPTY_SCHEDULE);

  useEffect(() => {
    loadStats();
    loadSchedules();
  }, []);

  const loadStats      = () => getScrapeStats().then(setStats).catch(() => {});
  const loadSchedules  = () => getSchedules().then(d => setSchedules(d.schedules || {})).catch(() => {});

  const toggleSource = (src) =>
    setSelected(s => s.includes(src) ? s.filter(x => x !== src) : [...s, src]);

  const handleScrapeAll = async () => {
    setLoading(true); setResults(null);
    try {
      const data = await scrapeAll();
      setResults(data);
      await loadStats();
      success(`Scraped ${data.summary?.total_saved ?? 0} opportunities`);
    } catch (e) { notifyError(e.message); }
    finally { setLoading(false); }
  };

  const handleScrapeOne = async () => {
    if (selected.length !== 1) return;
    setLoading(true); setResults(null);
    try {
      const data = await scrapeSource(selected[0]);
      setResults({ timestamp: data.timestamp, sources: { [data.source]: data }, summary: { total_scraped: data.scraped, total_saved: data.saved, total_failed: data.failed } });
      await loadStats();
      success(`Scraped ${data.saved ?? 0} from ${selected[0]}`);
    } catch (e) { notifyError(e.message); }
    finally { setLoading(false); }
  };

  const handleSync = async () => {
    setSyncLoading(true);
    try {
      const data = await syncNotion();
      success(`Synced ${data.synced?.length ?? 0} opportunities to Notion`);
      if (data.failed?.length) info(`${data.failed.length} failed to sync`);
    } catch (e) { notifyError(e.message || 'Notion not configured'); }
    finally { setSyncLoading(false); }
  };

  const handleCreateSchedule = async () => {
    if (!form.name.trim()) { notifyError('Schedule name required'); return; }
    setLoading(true);
    try {
      await createSchedule(form);
      success(`Schedule "${form.name}" created`);
      setForm(EMPTY_SCHEDULE);
      setShowForm(false);
      await loadSchedules();
    } catch (e) { notifyError(e.message); }
    finally { setLoading(false); }
  };

  const handleDeleteSchedule = async (name) => {
    setLoading(true);
    try {
      await deleteSchedule(name);
      success(`Schedule "${name}" deleted`);
      await loadSchedules();
    } catch (e) { notifyError(e.message); }
    finally { setLoading(false); }
  };

  const handleToggleSchedule = async (name, active) => {
    try {
      await updateSchedule(name, { enabled: !active });
      await loadSchedules();
    } catch (e) { notifyError(e.message); }
  };

  const allSelected  = selected.length === SOURCES.length;
  const noneSelected = selected.length === 0;

  return (
    <div className="scrape-page">
      <div className="page-header">
        <h1 className="page-title"><FaDownload /> Web Scraper</h1>
        <p className="page-subtitle">Fetch consultancy opportunities from multiple platforms</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="scrape-stats">
          <div className="stat-chip">
            <span>Total in DB</span>
            <strong>{stats.total_opportunities}</strong>
          </div>
          {Object.entries(stats.by_source || {}).map(([src, cnt]) => (
            <div key={src} className="stat-chip">
              <span>{src}</span>
              <strong>{cnt}</strong>
            </div>
          ))}
          {stats.last_scrape && (
            <div className="stat-chip stat-chip--muted">
              <span>Last scrape</span>
              <strong>{new Date(stats.last_scrape).toLocaleString()}</strong>
            </div>
          )}
        </div>
      )}

      {/* Source selection */}
      <div className="section">
        <div className="section-header-row">
          <h2 className="section-title">Select Sources</h2>
          <div className="select-actions">
            <button className="btn btn-ghost btn-sm" onClick={() => setSelected(SOURCES.map(s => s.value))} disabled={allSelected}>Select All</button>
            <button className="btn btn-ghost btn-sm" onClick={() => setSelected([])} disabled={noneSelected}>Clear</button>
          </div>
        </div>
        <div className="source-grid">
          {SOURCES.map(src => (
            <label key={src.value} className={`source-card${selected.includes(src.value) ? ' source-card--on' : ''}`}
              style={{ '--src-color': src.color }}>
              <input type="checkbox" checked={selected.includes(src.value)} onChange={() => toggleSource(src.value)} />
              <div className="source-dot" />
              <span>{src.value}</span>
              {selected.includes(src.value) && <FaCheck className="source-check" />}
            </label>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="scrape-actions">
        <button className="btn btn-primary" onClick={handleScrapeAll} disabled={loading || noneSelected}>
          {loading ? <><FaSpinner className="spin" /> Scraping…</> : <><FaDownload /> Scrape All Sources</>}
        </button>
        {selected.length === 1 && (
          <button className="btn btn-secondary" onClick={handleScrapeOne} disabled={loading}>
            {loading ? <><FaSpinner className="spin" /> Scraping…</> : <><FaDownload /> Scrape {selected[0]}</>}
          </button>
        )}
        <button className="btn btn-ghost" onClick={handleSync} disabled={syncLoading}>
          {syncLoading ? <><FaSpinner className="spin" /> Syncing…</> : <><FaSyncAlt /> Sync to Notion</>}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="section">
          <h2 className="section-title">Scrape Results</h2>
          <div className="results-summary">
            <div className="res-chip"><span>Scraped</span><strong>{results.summary?.total_scraped ?? 0}</strong></div>
            <div className="res-chip res-chip--success"><span>Saved</span><strong>{results.summary?.total_saved ?? 0}</strong></div>
            <div className="res-chip res-chip--danger"><span>Failed</span><strong>{results.summary?.total_failed ?? 0}</strong></div>
          </div>
          <div className="results-detail">
            {Object.entries(results.sources || {}).map(([src, d]) => (
              <div key={src} className={`result-row${d.status === 'failed' ? ' result-row--error' : ''}`}>
                <span className="result-src">{src}</span>
                <span>Scraped: <strong>{d.scraped ?? 0}</strong></span>
                <span>Saved: <strong>{d.saved ?? 0}</strong></span>
                {d.error && <span className="text-danger">{d.error}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Schedules */}
      <div className="section">
        <div className="section-header-row">
          <h2 className="section-title">Automated Scheduling</h2>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowForm(v => !v)}>
            {showForm ? <><FaTimes /> Cancel</> : '+ New Schedule'}
          </button>
        </div>

        {showForm && (
          <div className="schedule-form">
            <div className="form-row form-row-2">
              <div className="form-group">
                <label className="form-label">Schedule Name</label>
                <input className="form-control" placeholder="e.g. Daily Morning" value={form.name}
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Type</label>
                <select className="form-control" value={form.type}
                  onChange={e => setForm(f => ({ ...f, type: e.target.value }))}>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="interval">Interval (hours)</option>
                </select>
              </div>
            </div>

            <div className="form-row form-row-2">
              {form.type !== 'interval' && (
                <div className="form-group">
                  <label className="form-label">Time</label>
                  <input type="time" className="form-control" value={form.time}
                    onChange={e => setForm(f => ({ ...f, time: e.target.value }))} />
                </div>
              )}
              {form.type === 'weekly' && (
                <div className="form-group">
                  <label className="form-label">Day</label>
                  <select className="form-control" value={form.day_of_week}
                    onChange={e => setForm(f => ({ ...f, day_of_week: +e.target.value }))}>
                    {['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].map((d, i) =>
                      <option key={d} value={i}>{d}</option>)}
                  </select>
                </div>
              )}
              {form.type === 'interval' && (
                <div className="form-group">
                  <label className="form-label">Interval (hours)</label>
                  <input type="number" className="form-control" min={1} max={720} value={form.interval_hours}
                    onChange={e => setForm(f => ({ ...f, interval_hours: +e.target.value }))} />
                </div>
              )}
            </div>

            <button className="btn btn-primary btn-sm" onClick={handleCreateSchedule} disabled={loading}>
              {loading ? <><FaSpinner className="spin" /> Creating…</> : 'Create Schedule'}
            </button>
          </div>
        )}

        {Object.keys(schedules).length > 0 ? (
          <div className="schedule-list">
            {Object.entries(schedules).map(([name, sch]) => (
              <div key={name} className="schedule-item">
                <div className="schedule-info">
                  <strong>{name}</strong>
                  <span className="text-muted text-sm">
                    {sch.type === 'interval'
                      ? `Every ${sch.interval_hours}h`
                      : `${sch.type} @ ${sch.time}`}
                  </span>
                  {sch.next_run && (
                    <span className="text-muted text-xs">Next: {new Date(sch.next_run).toLocaleString()}</span>
                  )}
                </div>
                <div className="schedule-actions">
                  <button
                    className={`btn btn-sm ${sch.active ? 'btn-success' : 'btn-ghost'}`}
                    onClick={() => handleToggleSchedule(name, sch.active)}
                  >
                    {sch.active ? <><FaCheck /> Active</> : 'Inactive'}
                  </button>
                  <button className="btn btn-danger btn-sm btn-icon" onClick={() => handleDeleteSchedule(name)} aria-label="Delete">
                    <FaTrash />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : !showForm && (
          <p className="text-muted text-sm" style={{ marginTop: '0.75rem' }}>No schedules yet. Create one to automate scraping.</p>
        )}
      </div>

      {/* Instructions */}
      <div className="info-section">
        <h3>How to use</h3>
        <ol className="steps">
          {['Select one or more source platforms', 'Click "Scrape All Sources" to fetch opportunities', 'Results are saved automatically to your database', 'Sync to Notion for external sharing', 'Use Automated Scheduling for hands-free operation'].map((s, i) => (
            <li key={i}><span className="step-num">{i + 1}</span>{s}</li>
          ))}
        </ol>
      </div>
    </div>
  );
}
