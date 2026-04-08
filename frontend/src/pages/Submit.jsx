import React, { useState } from 'react';
import '../styles/Submit.css';

const Submit = () => {
  const [formData, setFormData] = useState({
    title: '',
    organization: '',
    url: '',
    description: '',
    priority: 'Medium',
    source_platform: 'Mock Data',
  });
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');

    try {
      const response = await fetch('http://localhost:5000/api/opportunities', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to submit opportunity');
      }

      const result = await response.json();
      setSuccessMessage('✓ Opportunity submitted successfully!');
      
      // Reset form
      setFormData({
        title: '',
        organization: '',
        url: '',
        description: '',
        priority: 'Medium',
        source_platform: 'Mock Data',
      });

      // Clear message after 5 seconds
      setTimeout(() => setSuccessMessage(''), 5000);
    } catch (err) {
      console.error('Error submitting opportunity:', err);
      setErrorMessage('Failed to submit. Make sure the backend is running on http://localhost:5000');
      setTimeout(() => setErrorMessage(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="submit-page">
      <h1>Submit an Opportunity</h1>
      {successMessage && <div className="success-message">{successMessage}</div>}
      {errorMessage && <div className="error-message">{errorMessage}</div>}
      
      <form onSubmit={handleSubmit} className="submit-form">
        <div className="form-group">
          <label htmlFor="title">Opportunity Title *</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="e.g., Senior Data Analyst"
          />
        </div>

        <div className="form-group">
          <label htmlFor="organization">Organization/Company *</label>
          <input
            type="text"
            id="organization"
            name="organization"
            value={formData.organization}
            onChange={handleChange}
            required
            placeholder="e.g., UNDP Africa"
          />
        </div>

        <div className="form-group">
          <label htmlFor="url">URL *</label>
          <input
            type="url"
            id="url"
            name="url"
            value={formData.url}
            onChange={handleChange}
            required
            placeholder="https://example.com/job"
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description *</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            placeholder="Describe the opportunity..."
            rows="6"
          />
        </div>

        <div className="form-group">
          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
          >
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="source_platform">Source Platform</label>
          <select
            id="source_platform"
            name="source_platform"
            value={formData.source_platform}
            onChange={handleChange}
          >
            <option value="Mock Data">User Submitted</option>
            <option value="Devex">Devex</option>
            <option value="Impactpool">Impactpool</option>
            <option value="UNDP">UNDP</option>
            <option value="World Bank">World Bank</option>
          </select>
        </div>

        <button 
          type="submit" 
          className="submit-btn"
          disabled={loading}
        >
          {loading ? 'Submitting...' : 'Submit Opportunity'}
        </button>
      </form>
    </div>
  );
};

export default Submit;
