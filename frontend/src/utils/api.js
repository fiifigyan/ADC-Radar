const BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

async function request(path, options = {}) {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });

  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      message = body.error || body.message || message;
    } catch {
      // ignore parse failure
    }
    throw new Error(message);
  }

  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

export const api = {
  get:    (path)        => request(path),
  post:   (path, body)  => request(path, { method: 'POST',   body: JSON.stringify(body) }),
  put:    (path, body)  => request(path, { method: 'PUT',    body: JSON.stringify(body) }),
  delete: (path)        => request(path, { method: 'DELETE' }),
};

// Domain helpers
export const getOpportunities = () =>
  api.get('/api/opportunities').then(r => r.data ?? r);

export const getOpportunity   = (id) => api.get(`/api/opportunities/${id}`);
export const createOpportunity = (data) => api.post('/api/opportunities', data);
export const getScrapeStats   = () => api.get('/api/scrape/stats');
export const scrapeAll        = (maxResults = 50) => api.post(`/api/scrape?max_results=${maxResults}`);
export const scrapeSource     = (source, maxResults = 50) =>
  api.post(`/api/scrape/${encodeURIComponent(source)}?max_results=${maxResults}`);
export const getSchedules     = () => api.get('/api/schedules');
export const createSchedule   = (data) => api.post('/api/schedules', data);
export const updateSchedule   = (name, data) => api.put(`/api/schedules/${name}`, data);
export const deleteSchedule   = (name) => api.delete(`/api/schedules/${name}`);
export const getAiStatus      = () => api.get('/api/ai/status');
export const analyzeAll       = () => api.post('/api/analyze/batch/all');
export const analyzeBySource  = (source) => api.post('/api/analyze/batch/by-source', { source });
export const analyzeSingle    = (id) => api.post(`/api/analyze/${id}`);
export const syncNotion       = () => api.post('/api/notion/sync');
export const notionStatus     = () => api.get('/api/notion/status');
export const healthCheck      = () => api.get('/health');
