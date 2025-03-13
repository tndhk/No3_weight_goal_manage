import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// API クライアントの作成
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 体重目標を取得
export const fetchWeightGoals = async (activeOnly = false) => {
  try {
    const response = await apiClient.get(`/api/fit/goal?active_only=${activeOnly}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching weight goals:', error);
    throw error;
  }
};

// 特定の体重目標を取得
export const fetchWeightGoal = async (goalId) => {
  try {
    const response = await apiClient.get(`/api/fit/goal/${goalId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching weight goal with ID ${goalId}:`, error);
    throw error;
  }
};

// 新しい体重目標を作成
export const createWeightGoal = async (goalData) => {
  try {
    const response = await apiClient.post('/api/fit/goal', goalData);
    return response.data;
  } catch (error) {
    console.error('Error creating weight goal:', error);
    throw error;
  }
};

// 体重目標を更新
export const updateWeightGoal = async (goalId, goalData) => {
  try {
    const response = await apiClient.put(`/api/fit/goal/${goalId}`, goalData);
    return response.data;
  } catch (error) {
    console.error(`Error updating weight goal with ID ${goalId}:`, error);
    throw error;
  }
};

// 体重目標を削除
export const deleteWeightGoal = async (goalId) => {
  try {
    const response = await apiClient.delete(`/api/fit/goal/${goalId}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting weight goal with ID ${goalId}:`, error);
    throw error;
  }
};

// 実測値と目標の差分を取得
export const fetchWeightDiff = async (goalId = null) => {
  try {
    let url = '/api/fit/weight/diff';
    if (goalId) {
      url += `?goal_id=${goalId}`;
    }
    
    const response = await apiClient.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching weight diff:', error);
    throw error;
  }
};

// 体重予測データを取得
export const fetchWeightProjection = async (goalId = null, days = 30) => {
  try {
    let url = `/api/fit/weight/projection?days=${days}`;
    if (goalId) {
      url += `&goal_id=${goalId}`;
    }
    
    const response = await apiClient.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching weight projection:', error);
    throw error;
  }
};