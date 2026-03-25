import React from 'react';
import { opportunities } from '../mockData';
import '../styles/Dashboard.css';

const Dashboard = () => {
  return (
    <main className="dashboard">
      <div className="search-container">
        <input type="text" placeholder="Search for opportunities..." />
        <button>Search</button>
      </div>
      <div className="opportunities-grid">
        {opportunities.map((opp) => (
          <div key={opp.id} className="opportunity-card">
            <div className="card-header">
              <h3>{opp.title}</h3>
              <span className={`priority-${opp.priority.toLowerCase()}`}>{opp.priority}</span>
            </div>
            <div className="card-body">
              <p><strong>Organization:</strong> {opp.organization}</p>
              <p><strong>Source:</strong> {opp.source_platform}</p>
              <p><strong>Deadline:</strong> {opp.deadline}</p>
            </div>
            <div className="card-footer">
              <a href={opp.url} target="_blank" rel="noopener noreferrer" className="view-link">
                View More
              </a>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
};

export default Dashboard;