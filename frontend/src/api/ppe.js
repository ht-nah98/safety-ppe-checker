import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkPPE(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);
  const res = await axios.post(`${API_BASE}/api/v1/check-ppe`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30000,
  });
  return res.data;
}

export async function getInspections(limit = 20, offset = 0) {
  const res = await axios.get(`${API_BASE}/api/v1/inspections`, {
    params: { limit, offset },
  });
  return res.data;
}

export async function getInspectionById(id) {
  const res = await axios.get(`${API_BASE}/api/v1/inspections/${id}`);
  return res.data;
}

export async function getStats() {
  const res = await axios.get(`${API_BASE}/api/v1/stats`);
  return res.data;
}

export function getExportUrl() {
  return `${API_BASE}/api/v1/inspections/export`;
}
export async function getHealth() {
  const res = await axios.get(`${API_BASE}/health`);
  return res.data;
}
