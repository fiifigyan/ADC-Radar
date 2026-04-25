import { useState } from 'react';
import { FaPaperPlane, FaSpinner } from 'react-icons/fa';
import { useNotification } from '../contexts/NotificationContext';
import { createOpportunity } from '../utils/api';
import '../styles/Submit.css';

const EMPTY = { title: '', organization: '', url: '', description: '', priority: 'Medium', source_platform: 'Mock Data' };

export default function Submit() {
  const { success, error: notifyError } = useNotification();
  const [form, setForm] = useState(EMPTY);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const set = (k, v) => { setForm(f => ({ ...f, [k]: v })); setErrors(e => ({ ...e, [k]: '' })); };

  const validate = () => {
    const e = {};
    if (!form.title.trim())        e.title = 'Title is required';
    if (!form.organization.trim()) e.organization = 'Organization is required';
    if (!form.description.trim())  e.description = 'Description is required';
    if (form.url && !form.url.startsWith('http')) e.url = 'URL must start with http:// or https://';
    setErrors(e);
    return !Object.keys(e).length;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      await createOpportunity(form);
      success('Opportunity submitted successfully!');
      setForm(EMPTY);
      setErrors({});
    } catch (err) {
      notifyError(err.message || 'Failed to submit. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const Field = ({ label, name, ...props }) => (
    <div className="form-group">
      <label className="form-label" htmlFor={name}>{label}</label>
      <input
        id={name} name={name} className={`form-control${errors[name] ? ' form-control--error' : ''}`}
        value={form[name]} onChange={e => set(name, e.target.value)} {...props}
      />
      {errors[name] && <span className="field-error">{errors[name]}</span>}
    </div>
  );

  return (
    <div className="submit-page">
      <div className="page-header">
        <h1 className="page-title"><FaPaperPlane /> Submit an Opportunity</h1>
        <p className="page-subtitle">Manually add an opportunity to the database</p>
      </div>

      <div className="submit-card">
        <form onSubmit={handleSubmit} noValidate>
          <Field label="Opportunity Title *" name="title" placeholder="e.g. Senior Data Analyst" maxLength={300} />
          <Field label="Organization *" name="organization" placeholder="e.g. UNDP Africa" maxLength={200} />
          <Field label="URL" name="url" type="url" placeholder="https://example.com/job" />

          <div className="form-group">
            <label className="form-label" htmlFor="description">Description *</label>
            <textarea
              id="description" className={`form-control${errors.description ? ' form-control--error' : ''}`}
              value={form.description} onChange={e => set('description', e.target.value)}
              placeholder="Describe the opportunity, responsibilities, requirements…"
              rows={6}
            />
            {errors.description && <span className="field-error">{errors.description}</span>}
            <span className="field-hint">{form.description.length} characters</span>
          </div>

          <div className="form-row form-row-2">
            <div className="form-group">
              <label className="form-label" htmlFor="priority">Priority</label>
              <select id="priority" className="form-control" value={form.priority} onChange={e => set('priority', e.target.value)}>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="source_platform">Source</label>
              <select id="source_platform" className="form-control" value={form.source_platform} onChange={e => set('source_platform', e.target.value)}>
                <option value="Mock Data">User Submitted</option>
                <option value="Devex">Devex</option>
                <option value="Impactpool">Impactpool</option>
                <option value="UNDP">UNDP</option>
                <option value="World Bank">World Bank</option>
                <option value="DevelopmentAid">DevelopmentAid</option>
              </select>
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-lg submit-btn" disabled={loading}>
            {loading ? <><FaSpinner className="spin" /> Submitting…</> : <><FaPaperPlane /> Submit Opportunity</>}
          </button>
        </form>
      </div>
    </div>
  );
}
