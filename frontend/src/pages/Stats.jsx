import { useEffect, useMemo, useState } from 'react';
import { FaChartBar, FaDatabase, FaRobot, FaStar } from 'react-icons/fa';
import { getOpportunities } from '../utils/api';
import '../styles/Stats.css';

const SOURCE_COLORS = {
  Devex: '#EC4899', Impactpool: '#6366F1', UNDP: '#06B6D4',
  'World Bank': '#3B82F6', DevelopmentAid: '#8B5CF6', 'Mock Data': '#6B7280',
};

export default function Stats() {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getOpportunities()
      .then(setOpportunities)
      .finally(() => setLoading(false));
  }, []);

  const stats = useMemo(() => {
    if (!opportunities.length) return null;
    const analyzed    = opportunities.filter(o => o.processed_at);
    const avgRelevance = analyzed.length
      ? Math.round(analyzed.reduce((s, o) => s + (o.relevance_score || 0), 0) / analyzed.length)
      : 0;

    const bySource   = {};
    const byPriority = { High: 0, Medium: 0, Low: 0 };
    const byRegion   = {};
    const byDeadline = {};
    const skillCount = {};

    opportunities.forEach(o => {
      bySource[o.source_platform] = (bySource[o.source_platform] || 0) + 1;
      if (o.priority) byPriority[o.priority] = (byPriority[o.priority] || 0) + 1;
      (o.regions || []).forEach(r => { byRegion[r] = (byRegion[r] || 0) + 1; });
      if (o.deadline) {
        const m = new Date(o.deadline).toLocaleString('default', { month: 'short', year: 'numeric' });
        byDeadline[m] = (byDeadline[m] || 0) + 1;
      }
      [...(o.primary_skills || []), ...(o.secondary_skills || [])].forEach(s => {
        skillCount[s] = (skillCount[s] || 0) + 1;
      });
    });

    const topSkills = Object.entries(skillCount).sort((a, b) => b[1] - a[1]).slice(0, 10);
    const sourceMax = Math.max(...Object.values(bySource), 1);

    return { analyzed: analyzed.length, avgRelevance, bySource, byPriority, byRegion, byDeadline, topSkills, sourceMax };
  }, [opportunities]);

  if (loading) return (
    <div className="stats-page">
      <div className="page-header">
        <h1 className="page-title"><FaChartBar /> Analytics Dashboard</h1>
      </div>
      <div className="kpi-grid">
        {[...Array(4)].map((_, i) => <div key={i} className="skeleton" style={{ height: 120, borderRadius: 12 }} />)}
      </div>
    </div>
  );

  if (!stats) return (
    <div className="stats-page">
      <div className="page-header">
        <h1 className="page-title"><FaChartBar /> Analytics Dashboard</h1>
        <p className="page-subtitle">No data yet — scrape opportunities first.</p>
      </div>
    </div>
  );

  const regionEntries  = Object.entries(stats.byRegion).sort((a, b) => b[1] - a[1]);
  const deadlineEntries = Object.entries(stats.byDeadline).sort((a, b) => new Date(a[0]) - new Date(b[0]));
  const total = opportunities.length;
  const regionMax = Math.max(...regionEntries.map(r => r[1]), 1);
  const deadlineMax = Math.max(...deadlineEntries.map(d => d[1]), 1);

  return (
    <div className="stats-page">
      <div className="page-header">
        <h1 className="page-title"><FaChartBar /> Analytics Dashboard</h1>
        <p className="page-subtitle">Real-time insights from your opportunities database</p>
      </div>

      {/* KPIs */}
      <div className="kpi-grid">
        <KpiCard icon={<FaDatabase />} label="Total" value={total} sub="opportunities" color="accent" />
        <KpiCard icon={<FaRobot />} label="Analyzed" value={stats.analyzed}
          sub={`${total ? Math.round((stats.analyzed / total) * 100) : 0}% of total`} color="success"
          progress={total ? stats.analyzed / total : 0}
        />
        <KpiCard icon={<FaDatabase />} label="Unanalyzed" value={total - stats.analyzed}
          sub="pending AI analysis" color="warning" />
        <KpiCard icon={<FaStar />} label="Avg Relevance" value={`${stats.avgRelevance}%`}
          sub="from AI analysis" color="info" />
      </div>

      {/* Charts row 1 */}
      <div className="charts-row">
        <div className="chart-card">
          <h2 className="chart-title">By Source</h2>
          <div className="bar-list">
            {Object.entries(stats.bySource).map(([src, count]) => (
              <div key={src} className="bar-item">
                <span className="bar-label">{src}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${(count / stats.sourceMax) * 100}%`, background: SOURCE_COLORS[src] || '#6B7280' }} />
                </div>
                <span className="bar-val">{count}</span>
              </div>
            ))}
            {!Object.keys(stats.bySource).length && <p className="text-muted text-sm">No source data</p>}
          </div>
        </div>

        <div className="chart-card">
          <h2 className="chart-title">Priority Distribution</h2>
          <div className="priority-vis">
            {[
              { key: 'High',   color: 'var(--danger)',  bg: 'var(--danger-light)' },
              { key: 'Medium', color: 'var(--warning)', bg: 'var(--warning-light)' },
              { key: 'Low',    color: 'var(--info)',    bg: 'var(--info-light)' },
            ].map(({ key, color, bg }) => (
              <div key={key} className="priority-row" style={{ '--p-color': color, '--p-bg': bg }}>
                <div className="priority-pill">{key}</div>
                <div className="priority-bar-track">
                  <div className="priority-bar-fill"
                    style={{ width: `${total ? ((stats.byPriority[key] || 0) / total) * 100 : 0}%` }} />
                </div>
                <span className="priority-count">{stats.byPriority[key] || 0}</span>
                <span className="priority-pct">
                  {total ? ((stats.byPriority[key] || 0) / total * 100).toFixed(1) : 0}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Charts row 2 */}
      <div className="charts-row">
        <div className="chart-card">
          <h2 className="chart-title">By Region</h2>
          {regionEntries.length ? (
            <div className="bar-list">
              {regionEntries.map(([region, count]) => (
                <div key={region} className="bar-item">
                  <span className="bar-label">{region}</span>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${(count / regionMax) * 100}%`, background: 'var(--accent)' }} />
                  </div>
                  <span className="bar-val">{count}</span>
                </div>
              ))}
            </div>
          ) : <p className="text-muted text-sm">No region data — analyze opportunities first.</p>}
        </div>

        <div className="chart-card">
          <h2 className="chart-title">Deadline Timeline</h2>
          {deadlineEntries.length ? (
            <div className="bar-list">
              {deadlineEntries.map(([month, count]) => (
                <div key={month} className="bar-item">
                  <span className="bar-label">{month}</span>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${(count / deadlineMax) * 100}%`, background: 'var(--primary)' }} />
                  </div>
                  <span className="bar-val">{count}</span>
                </div>
              ))}
            </div>
          ) : <p className="text-muted text-sm">No deadline data available.</p>}
        </div>
      </div>

      {/* Skills */}
      <div className="chart-card">
        <h2 className="chart-title">Top 10 Required Skills</h2>
        {stats.topSkills.length ? (
          <div className="skills-grid">
            {stats.topSkills.map(([skill, count]) => (
              <div key={skill} className="skill-pill">
                <span className="skill-name">{skill}</span>
                <span className="skill-count">{count}</span>
              </div>
            ))}
          </div>
        ) : <p className="text-muted text-sm">No skill data — analyze opportunities first.</p>}
      </div>

      {/* Summary */}
      <div className="stats-summary">
        <h2 className="chart-title">Summary</h2>
        <ul className="summary-list">
          <li><strong>Data quality:</strong> {stats.analyzed} / {total} opportunities AI-analyzed</li>
          <li><strong>Top source:</strong> {Object.entries(stats.bySource).sort((a,b)=>b[1]-a[1])[0]?.[0] ?? '—'}</li>
          <li><strong>Average relevance:</strong> {stats.avgRelevance}% — measures overall opportunity fit</li>
          <li><strong>High-priority:</strong> {stats.byPriority.High || 0} opportunities flagged</li>
          <li><strong>Geographic spread:</strong> {Object.keys(stats.byRegion).length} regions covered</li>
        </ul>
      </div>
    </div>
  );
}

function KpiCard({ icon, label, value, sub, color, progress }) {
  return (
    <div className={`kpi-card kpi-${color}`}>
      <div className="kpi-icon" aria-hidden="true">{icon}</div>
      <div className="kpi-body">
        <p className="kpi-label">{label}</p>
        <p className="kpi-value">{value}</p>
        {progress !== undefined && (
          <div className="kpi-progress">
            <div className="kpi-fill" style={{ width: `${Math.round(progress * 100)}%` }} />
          </div>
        )}
        <p className="kpi-sub">{sub}</p>
      </div>
    </div>
  );
}
