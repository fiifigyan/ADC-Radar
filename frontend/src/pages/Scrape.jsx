import React, { useState, useEffect } from 'react';
import '../styles/Scrape.css';

const Scrape = () => {
  const [loading, setLoading] = useState(false);
  const [selectedSources, setSelectedSources] = useState([
    'Devex',
    'Impactpool',
    'UNDP',
    'World Bank',
    'DevelopmentAid',
  ]);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [schedules, setSchedules] = useState([]);
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [scheduleForm, setScheduleForm] = useState({
    name: '',
    type: 'daily',
    time: '10:00',
    day_of_week: 0,
    interval_hours: 24,
    sources: [],
    enabled: true,
  });

  const sources = [
    { value: 'Devex', label: 'Devex', color: '#3498db' },
    { value: 'Impactpool', label: 'Impactpool', color: '#2ecc71' },
    { value: 'UNDP', label: 'UNDP', color: '#e74c3c' },
    { value: 'World Bank', label: 'World Bank', color: '#f39c12' },
    { value: 'DevelopmentAid', label: 'Development Aid', color: '#9b59b6' },
  ];

  useEffect(() => {
    fetchStats();
    loadSchedules();
  }, []);

  const loadSchedules = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/schedules');
      if (response.ok) {
        const data = await response.json();
        setSchedules(data.schedules || {});
      }
    } catch (err) {
      console.error('Error loading schedules:', err);
    }
  };

  const handleSourceChange = (source) => {
    if (selectedSources.includes(source)) {
      setSelectedSources(selectedSources.filter((s) => s !== source));
    } else {
      setSelectedSources([...selectedSources, source]);
    }
  };

  const scrapeAll = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('http://localhost:5000/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) throw new Error('Failed to initiate scraping');

      const data = await response.json();
      setResults(data);
      await fetchStats();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const scrapeSource = async (source) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const encodedSource = encodeURIComponent(source);
      const response = await fetch(`http://localhost:5000/api/scrape/${encodedSource}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) throw new Error(`Failed to scrape from ${source}`);

      const data = await response.json();
      
      // Transform the single source response to match the multi-source format
      const results = {
        timestamp: data.timestamp,
        sources: {
          [data.source]: {
            scraped: data.scraped,
            saved: data.saved,
            failed: data.failed,
            status: data.status,
            error: data.error || null,
          }
        },
        summary: {
          total_scraped: data.scraped,
          total_saved: data.saved,
          total_failed: data.failed,
        }
      };
      
      setResults(results);
      await fetchStats();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/scrape/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const createSchedule = async () => {
    if (!scheduleForm.name.trim()) {
      alert('Please enter a schedule name');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/schedules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scheduleForm),
      });

      if (response.ok) {
        setScheduleForm({
          name: '',
          type: 'daily',
          time: '10:00',
          day_of_week: 0,
          interval_hours: 24,
          sources: [],
          enabled: true,
        });
        setShowScheduleForm(false);
        await loadSchedules();
        alert('✓ Schedule created successfully!');
      } else {
        const data = await response.json();
        alert(`Error: ${data.message || 'Failed to create schedule'}`);
      }
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const deleteSchedule = async (name) => {
    if (!window.confirm(`Are you sure you want to delete the "${name}" schedule?`)) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/schedules/${name}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await loadSchedules();
        alert('✓ Schedule deleted successfully!');
      } else {
        alert('Failed to delete schedule');
      }
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const updateScheduleEnabled = async (name, enabled) => {
    try {
      const response = await fetch(`http://localhost:5000/api/schedules/${name}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !enabled }),
      });

      if (response.ok) {
        await loadSchedules();
      }
    } catch (err) {
      console.error('Error updating schedule:', err);
    }
  };

  const syncToNotion = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/notion/sync', {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to sync to Notion');

      const data = await response.json();
      alert(`✓ Synced ${data.synced.length} opportunities to Notion`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="scrape-page">
      <h1>🕷️ Scrape Opportunities</h1>
      <p className="subtitle">Automatically fetch job opportunities from multiple sources</p>

      {error && <div className="error-message">❌ {error}</div>}

      {/* Statistics Section */}
      {stats && (
        <div className="stats-section">
          <h2>📊 Current Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-label">Total Opportunities</span>
              <span className="stat-value">{stats.total_opportunities}</span>
            </div>
            {stats.by_source && Object.entries(stats.by_source).map(([source, count]) => (
              <div key={source} className="stat-card">
                <span className="stat-label">{source}</span>
                <span className="stat-value">{count}</span>
              </div>
            ))}
          </div>
          {stats.last_scrape && (
            <p className="last-scrape">
              Last scrape: {new Date(stats.last_scrape).toLocaleString()}
            </p>
          )}
        </div>
      )}

      {/* Source Selection */}
      <div className="sources-section">
        <h2>📌 Select Sources to Scrape</h2>
        <div className="sources-list">
          {sources.map((source) => (
            <label key={source.value} className="source-checkbox">
              <input
                type="checkbox"
                checked={selectedSources.includes(source.value)}
                onChange={() => handleSourceChange(source.value)}
                disabled={loading}
              />
              <span style={{ borderColor: source.color }}>
                {source.label}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="actions-section">
        <button
          className="btn btn-primary"
          onClick={scrapeAll}
          disabled={loading}
        >
          {loading ? '⏳ Scraping...' : '🚀 Scrape All Sources'}
        </button>

        {selectedSources.length === 1 && (
          <button
            className="btn btn-secondary"
            onClick={() => scrapeSource(selectedSources[0])}
            disabled={loading}
          >
            {loading ? '⏳ Scraping...' : `📥 Scrape ${selectedSources[0]}`}
          </button>
        )}

        <button
          className="btn btn-success"
          onClick={syncToNotion}
          disabled={loading}
        >
          {loading ? '⏳ Syncing...' : '💾 Sync to Notion'}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="results-section">
          <h2>✅ Scraping Results</h2>
          
          <div className="summary">
            <div className="summary-item">
              <span>Total Scraped:</span>
              <strong>{results.summary.total_scraped}</strong>
            </div>
            <div className="summary-item">
              <span>Successfully Saved:</span>
              <strong>{results.summary.total_saved}</strong>
            </div>
            <div className="summary-item">
              <span>Failed:</span>
              <strong className="error">{results.summary.total_failed}</strong>
            </div>
          </div>

          <h3>Details by Source</h3>
          <div className="sources-results">
            {Object.entries(results.sources || {}).map(([source, sourceData]) => (
              <div key={source} className="source-result">
                <h4>{source}</h4>
                <ul>
                  <li>Scraped: <strong>{sourceData.scraped || 0}</strong></li>
                  <li>Saved: <strong>{sourceData.saved || 0}</strong></li>
                  <li>Failed: <strong>{sourceData.failed || 0}</strong></li>
                  {sourceData.error && (
                    <li className="error">Error: {sourceData.error}</li>
                  )}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Schedule Management Section */}
      <div className="schedule-section">
        <div className="schedule-header">
          <h2>⏰ Automated Scheduling</h2>
          <button
            className="btn btn-secondary"
            onClick={() => setShowScheduleForm(!showScheduleForm)}
            disabled={loading}
          >
            {showScheduleForm ? '✕ Close' : '➕ Create Schedule'}
          </button>
        </div>

        {showScheduleForm && (
          <div className="schedule-form">
            <div className="form-group">
              <label>Schedule Name</label>
              <input
                type="text"
                placeholder="e.g., Daily Morning Scrape"
                value={scheduleForm.name}
                onChange={(e) =>
                  setScheduleForm({ ...scheduleForm, name: e.target.value })
                }
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Schedule Type</label>
                <select
                  value={scheduleForm.type}
                  onChange={(e) =>
                    setScheduleForm({ ...scheduleForm, type: e.target.value })
                  }
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="interval">Interval (Hours)</option>
                </select>
              </div>

              {scheduleForm.type !== 'interval' && (
                <div className="form-group">
                  <label>Time</label>
                  <input
                    type="time"
                    value={scheduleForm.time}
                    onChange={(e) =>
                      setScheduleForm({ ...scheduleForm, time: e.target.value })
                    }
                  />
                </div>
              )}

              {scheduleForm.type === 'weekly' && (
                <div className="form-group">
                  <label>Day of Week</label>
                  <select
                    value={scheduleForm.day_of_week}
                    onChange={(e) =>
                      setScheduleForm({
                        ...scheduleForm,
                        day_of_week: parseInt(e.target.value),
                      })
                    }
                  >
                    <option value={0}>Monday</option>
                    <option value={1}>Tuesday</option>
                    <option value={2}>Wednesday</option>
                    <option value={3}>Thursday</option>
                    <option value={4}>Friday</option>
                    <option value={5}>Saturday</option>
                    <option value={6}>Sunday</option>
                  </select>
                </div>
              )}

              {scheduleForm.type === 'interval' && (
                <div className="form-group">
                  <label>Interval (Hours)</label>
                  <input
                    type="number"
                    min="1"
                    max="720"
                    value={scheduleForm.interval_hours}
                    onChange={(e) =>
                      setScheduleForm({
                        ...scheduleForm,
                        interval_hours: parseInt(e.target.value),
                      })
                    }
                  />
                </div>
              )}
            </div>

            <div className="form-group">
              <label>Sources to Scrape (Optional - leave empty for all)</label>
              <div className="sources-checkboxes">
                {sources.map((source) => (
                  <label key={source.value} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={scheduleForm.sources.includes(source.value)}
                      onChange={(e) => {
                        const newSources = e.target.checked
                          ? [...scheduleForm.sources, source.value]
                          : scheduleForm.sources.filter((s) => s !== source.value);
                        setScheduleForm({ ...scheduleForm, sources: newSources });
                      }}
                    />
                    {source.label}
                  </label>
                ))}
              </div>
            </div>

            <button
              className="btn btn-success"
              onClick={createSchedule}
              disabled={loading}
            >
              {loading ? '⏳ Creating...' : '✓ Create Schedule'}
            </button>
          </div>
        )}

        {Object.keys(schedules).length > 0 && (
          <div className="schedules-list">
            <h3>Your Schedules</h3>
            <div className="schedule-items">
              {Object.entries(schedules).map(([name, schedule]) => (
                <div key={name} className="schedule-item">
                  <div className="schedule-info">
                    <h4>{name}</h4>
                    <p>
                      Type: <strong>{schedule.type.toUpperCase()}</strong>
                      {schedule.type !== 'interval' && ` @ ${schedule.time}`}
                      {schedule.type === 'interval' && ` - Every ${schedule.interval_hours} hours`}
                    </p>
                    {schedule.sources && schedule.sources.length > 0 && (
                      <p>Sources: <strong>{schedule.sources.join(', ')}</strong></p>
                    )}
                    {schedule.next_run && (
                      <p>Next Run: <strong>{new Date(schedule.next_run).toLocaleString()}</strong></p>
                    )}
                  </div>
                  <div className="schedule-actions">
                    <button
                      className={`btn-small ${schedule.active ? 'btn-active' : 'btn-inactive'}`}
                      onClick={() => updateScheduleEnabled(name, schedule.active)}
                      disabled={loading}
                    >
                      {schedule.active ? '✓ Active' : '✕ Inactive'}
                    </button>
                    <button
                      className="btn-small btn-delete"
                      onClick={() => deleteSchedule(name)}
                      disabled={loading}
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="info-box">
        <h3>ℹ️ How It Works</h3>
        <ul>
          <li>Select the sources you want to scrape from</li>
          <li>Click "Scrape All Sources" to fetch opportunities from all enabled sources</li>
          <li>Opportunities are automatically saved to the local database</li>
          <li>Click "Sync to Notion" to upload them to your Notion database</li>
          <li>Check the Dashboard to see all scraped opportunities</li>
        </ul>
      </div>
    </div>
  );
};

export default Scrape;
