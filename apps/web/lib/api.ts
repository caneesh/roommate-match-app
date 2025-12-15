import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Auth API
export const authAPI = {
  signup: (data: any) => api.post('/auth/signup', data),
  login: (data: any) => api.post('/auth/login', data),
  verify: () => api.get('/auth/verify'),
};

// Resident API
export const residentAPI = {
  getProfile: () => api.get('/resident/profile'),
  updateProfile: (data: any) => api.put('/resident/profile', data),
  submitQuestionnaire: (data: any) => api.post('/resident/questionnaire', data),
  getQuestionnaire: () => api.get('/resident/questionnaire'),
  getMatches: () => api.get('/resident/matches'),
  submitFeedback: (data: any) => api.post('/resident/feedback', data),
  deleteData: () => api.delete('/resident/data'),
};

// Operator API
export const operatorAPI = {
  getDashboard: () => api.get('/operator/dashboard'),
  createProperty: (data: any) => api.post('/operator/properties', data),
  listProperties: () => api.get('/operator/properties'),
  createUnit: (data: any) => api.post('/operator/units', data),
  listUnits: (propertyId: string) => api.get(`/operator/properties/${propertyId}/units`),
  createRoom: (data: any) => api.post('/operator/rooms', data),
  listApplicants: (propertyId?: string) =>
    api.get('/operator/applicants', { params: { property_id: propertyId } }),
  runMatching: (data: any) => api.post('/operator/match-runs', data),
  getMatchResults: (matchRunId: string) => api.get(`/operator/match-runs/${matchRunId}/results`),
  createMoveIn: (data: any) => api.post('/operator/move-ins', data),
  createConflictReport: (data: any) => api.post('/operator/conflict-reports', data),
  listConflictReports: () => api.get('/operator/conflict-reports'),
};

// Admin API
export const adminAPI = {
  listUsers: () => api.get('/admin/users'),
  listEvents: (limit?: number) => api.get('/admin/events', { params: { limit } }),
  getMetrics: () => api.get('/admin/metrics'),
  listAuditLogs: (limit?: number) => api.get('/admin/audit-logs', { params: { limit } }),
};

// Public API
export const publicAPI = {
  submitLead: (data: any) => api.post('/public/leads', data),
  health: () => api.get('/public/health'),
};
