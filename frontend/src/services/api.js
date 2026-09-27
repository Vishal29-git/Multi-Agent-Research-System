import axios from 'axios';

const API_BASE = '/api/research';

export const startResearch = async (query) => {
  const response = await axios.post(API_BASE, { query });
  return response.data;
};

export const listSessions = async () => {
  const response = await axios.get(API_BASE);
  return response.data;
};

export const getSessionDetail = async (id) => {
  const response = await axios.get(`${API_BASE}/${id}`);
  return response.data;
};

export const getSessionStatus = async (id) => {
  const response = await axios.get(`${API_BASE}/${id}/status`);
  return response.data;
};

export const getSessionSources = async (id) => {
  const response = await axios.get(`${API_BASE}/${id}/sources`);
  return response.data;
};

export const subscribeStatusSSE = (id, onEvent, onError) => {
  const eventSource = new EventSource(`${API_BASE}/${id}/stream`);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onEvent(data);
      if (data.status === 'completed' || data.status === 'failed') {
        eventSource.close();
      }
    } catch (err) {
      console.error('Error parsing SSE event:', err);
    }
  };

  eventSource.onerror = (err) => {
    console.warn('SSE stream error:', err);
    if (onError) onError(err);
    eventSource.close();
  };

  return () => {
    eventSource.close();
  };
};
