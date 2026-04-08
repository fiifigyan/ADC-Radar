import React, { useState, useEffect } from 'react';
import '../styles/Stats.css';

const Stats = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/opportunities');
      if (response.ok) {
        const data = await response.json();
        setOpportunities(data);
        calculateStats(data);
      }
    } catch (err) {
      console.error('Error loading opportunities:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (opps) => {
    const totalOpps = opps.length;
    const analyzed = opps.filter((o) => o.processed_at).length;
    const unanalyzed = totalOpps - analyzed;

    // By source
    const bySource = {};
    opps.forEach((o) => {
      bySource[o.source_platform] = (bySource[o.source_platform] || 0) + 1;
    });

    // By priority
    const byPriority = { High: 0, Medium: 0, Low: 0 };
    opps.forEach((o) => {
      if (o.priority) byPriority[o.priority]++;
    });

    // By region
    const byRegion = {};
    opps.forEach((o) => {
      if (o.regions && Array.isArray(o.regions)) {
        o.regions.forEach((region) => {
          byRegion[region] = (byRegion[region] || 0) + 1;
        });
      }
    });

    // Relevance score average
    const analyzedOpps = opps.filter((o) => o.relevance_score);
    const avgRelevance =
      analyzedOpps.length > 0
        ? Math.round(
            analyzedOpps.reduce((sum, o) => sum + (o.relevance_score || 0), 0) /
              analyzedOpps.length
          )
        : 0;

    // By deadline month
    const byDeadline = {};
    opps.forEach((o) => {
      if (o.deadline) {
        const date = new Date(o.deadline);
        const month = date.toLocaleString('default', { month: 'short', year: 'numeric' });
        byDeadline[month] = (byDeadline[month] || 0) + 1;
      }
    });

    // Top skills
    const skillCount = {};
    opps.forEach((o) => {
      const allSkills = [...(o.primary_skills || []), ...(o.secondary_skills || [])];
      allSkills.forEach((skill) => {
        skillCount[skill] = (skillCount[skill] || 0) + 1;
      });
    });

    const topSkills = Object.entries(skillCount)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    setStats({
      totalOpps,
      analyzed,
      unanalyzed,
      bySource,
      byPriority,
      byRegion,
      avgRelevance,
      byDeadline,
      topSkills,
    });
  };

  if (loading) {
    return <div className="stats-page">Loading statistics...</div>;
  }

  if (!stats) {
    return <div className="stats-page">No data available</div>;
  }

  const sourceEntries = Object.entries(stats.bySource);
  const sourceMax = Math.max(...sourceEntries.map(([, v]) => v), 1);

  const regionEntries = Object.entries(stats.byRegion).sort((a, b) => b[1] - a[1]);
  const deadlineEntries = Object.entries(stats.byDeadline).sort((a, b) => new Date(a[0]) - new Date(b[0]));

  return (
    <div className="stats-page">
      <h1>📊 Analytics Dashboard</h1>
      <p className="subtitle">Real-time insights from your opportunities database</p>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Opportunities</h3>
          <div className="metric-value">{stats.totalOpps}</div>
          <p className="metric-desc">All opportunities in database</p>
        </div>

        <div className="metric-card analyzed">
          <h3>Analyzed</h3>
          <div className="metric-value">{stats.analyzed}</div>
          <div className="metric-progress">
            <div
              className="progress-bar"
              style={{
                width: `${stats.totalOpps > 0 ? (stats.analyzed / stats.totalOpps) * 100 : 0}%`,
              }}
            />
          </div>
          <p className="metric-desc">
            {stats.totalOpps > 0 ? Math.round((stats.analyzed / stats.totalOpps) * 100) : 0}% analyzed
          </p>
        </div>

        <div className="metric-card unanalyzed">
          <h3>Unanalyzed</h3>
          <div className="metric-value">{stats.unanalyzed}</div>
          <p className="metric-desc">Pending AI analysis</p>
        </div>

        <div className="metric-card relevance">
          <h3>Avg Relevance</h3>
          <div className="metric-value">{stats.avgRelevance}%</div>
          <p className="metric-desc">Based on AI analysis</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        {/* Source Distribution */}
        <div className="chart-card">
          <h2>Opportunities by Source</h2>
          <div className="bar-chart">
            {sourceEntries.map(([source, count]) => (
              <div key={source} className="bar-item">
                <div className="bar-label">{source}</div>
                <div className="bar-container">
                  <div
                    className="bar-fill"
                    style={{ width: `${(count / sourceMax) * 100}%`, background: getSourceColor(source) }}
                  >
                    <span className="bar-value">{count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Priority Distribution */}
        <div className="chart-card">
          <h2>Priority Distribution</h2>
          <div className="priority-chart">
            <div className="priority-item high">
              <div className="priority-label">High</div>
              <div className="priority-count">{stats.byPriority.High}</div>
              <div className="priority-percent">
                {((stats.byPriority.High / stats.totalOpps) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="priority-item medium">
              <div className="priority-label">Medium</div>
              <div className="priority-count">{stats.byPriority.Medium}</div>
              <div className="priority-percent">
                {((stats.byPriority.Medium / stats.totalOpps) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="priority-item low">
              <div className="priority-label">Low</div>
              <div className="priority-count">{stats.byPriority.Low}</div>
              <div className="priority-percent">
                {((stats.byPriority.Low / stats.totalOpps) * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Two-Column Section */}
      <div className="two-column-section">
        {/* Opportunities by Region */}
        <div className="chart-card">
          <h2>Opportunities by Region</h2>
          <div className="region-list">
            {regionEntries.length > 0 ? (
              regionEntries.map(([region, count]) => (
                <div key={region} className="region-item">
                  <div className="region-name">{region}</div>
                  <div className="region-bar">
                    <div
                      className="region-fill"
                      style={{
                        width: `${(count / Math.max(...regionEntries.map((r) => r[1]))) * 100}%`,
                      }}
                    >
                      {count}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-data">No region data available</p>
            )}
          </div>
        </div>

        {/* Deadline Timeline */}
        <div className="chart-card">
          <h2>Deadline Timeline</h2>
          <div className="timeline-list">
            {deadlineEntries.length > 0 ? (
              deadlineEntries.map(([month, count]) => (
                <div key={month} className="timeline-item">
                  <div className="timeline-month">{month}</div>
                  <div className="timeline-bar">
                    <div
                      className="timeline-fill"
                      style={{
                        width: `${(count / Math.max(...deadlineEntries.map((d) => d[1]))) * 100}%`,
                      }}
                    >
                      {count}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-data">No deadline data available</p>
            )}
          </div>
        </div>
      </div>

      {/* Top Skills */}
      <div className="chart-card full-width">
        <h2>Top 10 Required Skills</h2>
        {stats.topSkills.length > 0 ? (
          <div className="skills-grid">
            {stats.topSkills.map(([skill, count]) => (
              <div key={skill} className="skill-tag">
                <div className="skill-name">{skill}</div>
                <div className="skill-count">{count}</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-data">No skill data available. Scrape and analyze opportunities to see skills.</p>
        )}
      </div>

      {/* Summary Section */}
      <div className="summary-section">
        <h2>📈 Summary</h2>
        <ul className="summary-list">
          <li>
            <strong>Data Quality:</strong> {stats.analyzed} out of {stats.totalOpps} opportunities have been
            AI-analyzed
          </li>
          <li>
            <strong>Most Common Source:</strong> {Object.entries(stats.bySource).sort((a, b) => b[1] - a[1])[0]?.[0]}
          </li>
          <li>
            <strong>Average Relevance:</strong> {stats.avgRelevance}% - shows overall opportunity quality
          </li>
          <li>
            <strong>Priority Focus:</strong> {stats.byPriority.High} high-priority opportunities identified
          </li>
          <li>
            <strong>Geographic Coverage:</strong> Opportunities covering {Object.keys(stats.byRegion).length} regions
          </li>
        </ul>
      </div>

      <div className="action-section">
        <p>💡 Tip: Analyze more opportunities in the Analyze page to improve statistics accuracy</p>
      </div>
    </div>
  );
};

function getSourceColor(source) {
  const colors = {
    Devex: '#3498db',
    Impactpool: '#2ecc71',
    UNDP: '#e74c3c',
    'World Bank': '#f39c12',
    DevelopmentAid: '#9b59b6',
    'Mock Data': '#95a5a6',
  };
  return colors[source] || '#34495e';
}

export default Stats;
