import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Fitbit認証状態の確認
export const checkFitbitStatus = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/fitbit/status`);
    return response.data;
  } catch (error) {
    console.error('Error checking Fitbit status:', error);
    throw error;
  }
};

// Fitbit認証のリダイレクトURL
export const getFitbitAuthUrl = () => {
  return `${API_URL}/api/fitbit/auth`;
};

// 体重データの取得
export const fetchFitbitWeight = async (fromDate, toDate) => {
  try {
    let url = `${API_URL}/api/fitbit/weight`;
    if (fromDate && toDate) {
      url += `?from_date=${fromDate}&to_date=${toDate}`;
    }
    
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching Fitbit weight data:', error);
    throw error;
  }
};

// 体重データの分析
export const analyzeFitbitWeight = async (fromDate, toDate) => {
  try {
    let url = `${API_URL}/api/fitbit/weight/analysis`;
    if (fromDate && toDate) {
      url += `?from_date=${fromDate}&to_date=${toDate}`;
    }
    
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('Error analyzing Fitbit weight data:', error);
    throw error;
  }
};