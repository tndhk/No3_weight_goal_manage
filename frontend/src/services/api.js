import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Fetch all data
export const fetchData = async () => {
  try {
    const response = await apiClient.get('/api/data');
    return response.data;
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
};

// Fetch analytics data
export const fetchAnalyticsData = async () => {
  try {
    const response = await apiClient.get('/api/analytics');
    return response.data;
  } catch (error) {
    console.error('Error fetching analytics data:', error);
    throw error;
  }
};

// Add new data
export const addData = async (data) => {
  try {
    const response = await apiClient.post('/api/data', data);
    return response.data;
  } catch (error) {
    console.error('Error adding data:', error);
    throw error;
  }
};

// Update existing data
export const updateData = async (id, data) => {
  try {
    const response = await apiClient.put(`/api/data/${id}`, data);
    return response.data;
  } catch (error) {
    console.error(`Error updating data with ID ${id}:`, error);
    throw error;
  }
};

// Delete data
export const deleteData = async (id) => {
  try {
    const response = await apiClient.delete(`/api/data/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting data with ID ${id}:`, error);
    throw error;
  }
};