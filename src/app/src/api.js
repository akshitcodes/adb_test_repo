import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});


export const getTodos = async (page = 1, page_size = 10) => {
  const response = await api.get(`/todos/?page=${page}&page_size=${page_size}`);
  return response.data;
};


export const postTodo = async (text) => {
  const response = await api.post('/todos/', { text });
  return response.data;
};

export default api;
