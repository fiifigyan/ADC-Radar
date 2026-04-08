import React, { useState, useEffect } from 'react';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [filteredOpportunities, setFilteredOpportunities] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filterPresets, setFilterPresets] = useState([]);
  const [currentPresetName, setCurrentPresetName] = useState('');

  // Advanced filters state
  const [filters, setFilters] = useState({
    priority: [],
    source: [],
    minRelevance: 0,
    maxRelevance: 100,
    minDeadline: '',
    maxDeadline: '',
    analyzed: 'all', // 'all', 'analyzed', 'unanalyzed'
    sortBy: 'deadline', // 'deadline', 'relevance', 'title', 'organization'
    sortOrder: 'asc', // 'asc', 'desc'
  });

  // Fetch opportunities from backend API
  useEffect(() => {
    const fetchOpportunities = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5000/api/opportunities');
        if (!response.ok) throw new Error('Failed to fetch opportunities');
        const data = await response.json();
        setOpportunities(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching opportunities:', err);
        setError('Failed to load opportunities. Make sure the backend is running on http://localhost:5000');
      } finally {
        setLoading(false);
      }
    };

    fetchOpportunities();
    loadFilterPresets();
  }, []);

  // Apply filters and search whenever they change
  useEffect(() => {
    applyFiltersAndSearch();
  }, [opportunities, searchQuery, filters]);

  // Get unique values for filter options
  const getPriorities = () => [...new Set(opportunities.map((o) => o.priority).filter(Boolean))];
  const getSources = () => [...new Set(opportunities.map((o) => o.source_platform).filter(Boolean))];

  // Apply all filters
  const applyFiltersAndSearch = () => {
    let result = opportunities;

    // Search filter
    if (searchQuery.trim()) {
      result = result.filter(
        (opp) =>
          opp.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          opp.organization?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          opp.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Priority filter
    if (filters.priority.length > 0) {
      result = result.filter((opp) => filters.priority.includes(opp.priority));
    }

    // Source filter
    if (filters.source.length > 0) {
      result = result.filter((opp) => filters.source.includes(opp.source_platform));
    }

    // Relevance score filter
    result = result.filter((opp) => {
      const score = opp.relevance_score || 0;
      return score >= filters.minRelevance && score <= filters.maxRelevance;
    });

    // Deadline filter
    if (filters.minDeadline) {
      result = result.filter((opp) => !opp.deadline || new Date(opp.deadline) >= new Date(filters.minDeadline));
    }
    if (filters.maxDeadline) {
      result = result.filter((opp) => !opp.deadline || new Date(opp.deadline) <= new Date(filters.maxDeadline));
    }

    // Analysis status filter
    if (filters.analyzed === 'analyzed') {
      result = result.filter((opp) => opp.processed_at);
    } else if (filters.analyzed === 'unanalyzed') {
      result = result.filter((opp) => !opp.processed_at);
    }

    // Sorting
    result.sort((a, b) => {
      let comparison = 0;
      switch (filters.sortBy) {
        case 'deadline':
          comparison = new Date(a.deadline || '9999-12-31') - new Date(b.deadline || '9999-12-31');
          break;
        case 'relevance':
          comparison = (b.relevance_score || 0) - (a.relevance_score || 0);
          break;
        case 'title':
          comparison = (a.title || '').localeCompare(b.title || '');
          break;
        case 'organization':
          comparison = (a.organization || '').localeCompare(b.organization || '');
          break;
        default:
          comparison = 0;
      }

      return filters.sortOrder === 'desc' ? -comparison : comparison;
    });

    setFilteredOpportunities(result);
  };

  // Handle filter changes
  const handleFilterChange = (filterName, value) => {
    setFilters((prev) => ({
      ...prev,
      [filterName]: value,
    }));
  };

  // Toggle multi-select filters
  const toggleFilter = (filterName, value) => {
    setFilters((prev) => {
      const current = prev[filterName];
      if (current.includes(value)) {
        return {
          ...prev,
          [filterName]: current.filter((v) => v !== value),
        };
      } else {
        return {
          ...prev,
          [filterName]: [...current, value],
        };
      }
    });
  };

  // Reset all filters
  const resetFilters = () => {
    setFilters({
      priority: [],
      source: [],
      minRelevance: 0,
      maxRelevance: 100,
      minDeadline: '',
      maxDeadline: '',
      analyzed: 'all',
      sortBy: 'deadline',
      sortOrder: 'asc',
    });
    setSearchQuery('');
    setCurrentPresetName('');
  };

  // Save filter preset
  const saveFilterPreset = () => {
    const name = prompt('Enter preset name:');
    if (name && name.trim()) {
      const newPreset = {
        id: Date.now(),
        name: name.trim(),
        filters: JSON.parse(JSON.stringify(filters)),
        searchQuery,
      };
      const presets = JSON.parse(localStorage.getItem('filterPresets') || '[]');
      presets.push(newPreset);
      localStorage.setItem('filterPresets', JSON.stringify(presets));
      setFilterPresets(presets);
      setCurrentPresetName(name.trim());
    }
  };

  // Load filter preset
  const loadFilterPreset = (preset) => {
    setFilters(preset.filters);
    setSearchQuery(preset.searchQuery);
    setCurrentPresetName(preset.name);
  };

  // Load presets from localStorage
  const loadFilterPresets = () => {
    const presets = JSON.parse(localStorage.getItem('filterPresets') || '[]');
    setFilterPresets(presets);
  };

  // Delete filter preset
  const deleteFilterPreset = (id) => {
    const updated = filterPresets.filter((p) => p.id !== id);
    localStorage.setItem('filterPresets', JSON.stringify(updated));
    setFilterPresets(updated);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    // Search is handled by useEffect
  };

  if (loading) {
    return <div className="dashboard"><p>Loading opportunities...</p></div>;
  }

  if (error) {
    return <div className="dashboard"><p style={{ color: 'red' }}>{error}</p></div>;
  }

  const activeFilterCount =
    filters.priority.length +
    filters.source.length +
    (filters.minRelevance > 0 || filters.maxRelevance < 100 ? 1 : 0) +
    (filters.minDeadline || filters.maxDeadline ? 1 : 0) +
    (filters.analyzed !== 'all' ? 1 : 0) +
    (searchQuery.trim() ? 1 : 0);

  return (
    <main className="dashboard">
      {/* Search Bar */}
      <div className="search-container">
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', width: '100%', gap: '10px' }}>
          <input
            type="text"
            placeholder="Search opportunities, organizations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ flex: 1 }}
          />
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className={`filter-btn ${showFilters ? 'active' : ''}`}
          >
            🔍 Filters {activeFilterCount > 0 && <span className="filter-badge">{activeFilterCount}</span>}
          </button>
        </form>
      </div>

      {/* Advanced Filters Panel */}
      {showFilters && (
        <div className="filters-panel">
          <div className="filters-header">
            <h3>Advanced Filters</h3>
            <button onClick={resetFilters} className="reset-btn">
              Reset All
            </button>
          </div>

          {/* Two-column filter layout */}
          <div className="filters-grid">
            {/* Priority Filter */}
            <div className="filter-section">
              <label>Priority</label>
              <div className="checkbox-group">
                {getPriorities().map((priority) => (
                  <label key={priority} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.priority.includes(priority)}
                      onChange={() => toggleFilter('priority', priority)}
                    />
                    {priority}
                  </label>
                ))}
              </div>
            </div>

            {/* Source Filter */}
            <div className="filter-section">
              <label>Source Platform</label>
              <div className="checkbox-group">
                {getSources().map((source) => (
                  <label key={source} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.source.includes(source)}
                      onChange={() => toggleFilter('source', source)}
                    />
                    {source}
                  </label>
                ))}
              </div>
            </div>

            {/* Relevance Score Filter */}
            <div className="filter-section">
              <label>
                Relevance Score: {filters.minRelevance} - {filters.maxRelevance}%
              </label>
              <div className="slider-group">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={filters.minRelevance}
                  onChange={(e) => handleFilterChange('minRelevance', parseInt(e.target.value))}
                  className="slider"
                />
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={filters.maxRelevance}
                  onChange={(e) => handleFilterChange('maxRelevance', parseInt(e.target.value))}
                  className="slider"
                />
              </div>
            </div>

            {/* Analysis Status Filter */}
            <div className="filter-section">
              <label>Analysis Status</label>
              <select
                value={filters.analyzed}
                onChange={(e) => handleFilterChange('analyzed', e.target.value)}
                className="filter-select"
              >
                <option value="all">All</option>
                <option value="analyzed">Analyzed ✓</option>
                <option value="unanalyzed">Unanalyzed</option>
              </select>
            </div>

            {/* Deadline Range Filter */}
            <div className="filter-section">
              <label>Deadline Range</label>
              <div className="date-range">
                <input
                  type="date"
                  value={filters.minDeadline}
                  onChange={(e) => handleFilterChange('minDeadline', e.target.value)}
                  placeholder="From"
                  className="filter-input"
                />
                <span>to</span>
                <input
                  type="date"
                  value={filters.maxDeadline}
                  onChange={(e) => handleFilterChange('maxDeadline', e.target.value)}
                  placeholder="To"
                  className="filter-input"
                />
              </div>
            </div>

            {/* Sort Options */}
            <div className="filter-section">
              <label>Sort By</label>
              <div className="sort-group">
                <select
                  value={filters.sortBy}
                  onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                  className="filter-select"
                >
                  <option value="deadline">Deadline</option>
                  <option value="relevance">Relevance Score</option>
                  <option value="title">Title</option>
                  <option value="organization">Organization</option>
                </select>
                <select
                  value={filters.sortOrder}
                  onChange={(e) => handleFilterChange('sortOrder', e.target.value)}
                  className="filter-select"
                >
                  <option value="asc">Ascending</option>
                  <option value="desc">Descending</option>
                </select>
              </div>
            </div>
          </div>

          {/* Preset Management */}
          <div className="preset-section">
            <h4>Filter Presets</h4>
            <div className="preset-controls">
              <button onClick={saveFilterPreset} className="preset-btn">
                💾 Save Current as Preset
              </button>
              {currentPresetName && (
                <span className="preset-name">Current: <strong>{currentPresetName}</strong></span>
              )}
            </div>
            {filterPresets.length > 0 && (
              <div className="preset-list">
                <p className="preset-label">Saved Presets:</p>
                <div className="preset-items">
                  {filterPresets.map((preset) => (
                    <div key={preset.id} className="preset-item">
                      <button
                        onClick={() => loadFilterPreset(preset)}
                        className={`preset-load-btn ${currentPresetName === preset.name ? 'active' : ''}`}
                      >
                        {preset.name}
                      </button>
                      <button
                        onClick={() => deleteFilterPreset(preset.id)}
                        className="preset-delete-btn"
                        title="Delete preset"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Results Summary */}
      <div className="opportunities-count">
        <p>
          Found <strong>{filteredOpportunities.length}</strong> opportunity/ies
          {opportunities.length !== filteredOpportunities.length && (
            <span> (out of {opportunities.length})</span>
          )}
        </p>
      </div>
      <div className="opportunities-grid">
        {filteredOpportunities.length > 0 ? (
          filteredOpportunities.map((opp) => (
            <div key={opp.id} className="opportunity-card">
              <div className="card-header">
                <div className="header-title">
                  <h3>{opp.title}</h3>
                  <span className={`priority-badge priority-${(opp.priority || 'low').toLowerCase()}`}>
                    {opp.priority || 'Unassigned'}
                  </span>
                </div>
                {opp.processed_at && (
                  <span className="analyzed-badge">✓ Analyzed</span>
                )}
              </div>

              <div className="card-body">
                <p className="org-info">
                  <strong>Organization:</strong> {opp.organization || 'Not specified'}
                </p>
                <p className="source-info">
                  <strong>Source:</strong> <span className="source-tag">{opp.source_platform}</span>
                </p>

                {opp.deadline && (
                  <p className="deadline-info">
                    <strong>Deadline:</strong> {new Date(opp.deadline).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </p>
                )}

                {opp.processed_at && (
                  <div className="ai-metrics">
                    {opp.relevance_score !== undefined && (
                      <div className="metric-item">
                        <span className="metric-label">Relevance:</span>
                        <div className="metric-bar">
                          <div
                            className="metric-fill"
                            style={{ width: `${opp.relevance_score}%` }}
                          />
                        </div>
                        <span className="metric-value">{opp.relevance_score}%</span>
                      </div>
                    )}
                    {opp.confidence_score !== undefined && (
                      <div className="metric-item">
                        <span className="metric-label">Confidence:</span>
                        <div className="metric-bar">
                          <div
                            className="metric-fill"
                            style={{ width: `${opp.confidence_score}%` }}
                          />
                        </div>
                        <span className="metric-value">{opp.confidence_score}%</span>
                      </div>
                    )}
                  </div>
                )}

                {opp.ai_summary && (
                  <p className="ai-summary">
                    <strong>AI Summary:</strong> {opp.ai_summary}
                  </p>
                )}
              </div>

              <div className="card-footer">
                {opp.url ? (
                  <a href={opp.url} target="_blank" rel="noopener noreferrer" className="view-link">
                    View Full Opportunity →
                  </a>
                ) : (
                  <span className="view-link disabled">No link available</span>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="no-results">
            <p>No opportunities found matching your filters.</p>
            <button onClick={resetFilters} className="reset-btn">
              Clear All Filters
            </button>
          </div>
        )}
      </div>
    </main>
  );
};

export default Dashboard;