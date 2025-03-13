import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { checkFitbitStatus, fetchFitbitWeight, analyzeFitbitWeight } from '../services/fitbitApi';
import { Line } from 'react-chartjs-2';

const FitbitDashboard = () => {
  const [authStatus, setAuthStatus] = useState({ loading: true, isAuthenticated: false });
  const [weightData, setWeightData] = useState({ loading: false, data: [], error: null });
  const [analysis, setAnalysis] = useState({ loading: false, data: null, error: null });
  const [dateRange, setDateRange] = useState({
    fromDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 過去30日
    toDate: new Date().toISOString().split('T')[0] // 今日
  });
  
  const navigate = useNavigate();
  
  // 認証状態の確認
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const result = await checkFitbitStatus();
        setAuthStatus({ 
          loading: false, 
          isAuthenticated: result.is_authenticated, 
          expiresAt: result.expires_at
        });
        
        // 認証されていない場合は接続ページへリダイレクト
        if (!result.is_authenticated) {
          navigate('/fitbit/connect');
        }
      } catch (err) {
        setAuthStatus({ loading: false, isAuthenticated: false });
        navigate('/fitbit/connect');
      }
    };
    
    checkAuth();
  }, [navigate]);
  
  // データの取得
  useEffect(() => {
    if (authStatus.isAuthenticated) {
      const loadData = async () => {
        setWeightData(prev => ({ ...prev, loading: true }));
        setAnalysis(prev => ({ ...prev, loading: true }));
        
        try {
          // 体重データの取得
          const weightResult = await fetchFitbitWeight(dateRange.fromDate, dateRange.toDate);
          setWeightData({ 
            loading: false, 
            data: weightResult.data, 
            error: null 
          });
          
          // 分析データの取得
          const analysisResult = await analyzeFitbitWeight(dateRange.fromDate, dateRange.toDate);
          setAnalysis({ 
            loading: false, 
            data: analysisResult.analysis, 
            error: null 
          });
        } catch (err) {
          setWeightData({ loading: false, data: [], error: 'Failed to fetch weight data' });
          setAnalysis({ loading: false, data: null, error: 'Failed to analyze weight data' });
        }
      };
      
      loadData();
    }
  }, [authStatus.isAuthenticated, dateRange]);
  
  // 日付範囲の変更
  const handleDateChange = (e) => {
    setDateRange({
      ...dateRange,
      [e.target.name]: e.target.value
    });
  };
  
  // データ更新
  const handleRefresh = async () => {
    if (authStatus.isAuthenticated) {
      setWeightData(prev => ({ ...prev, loading: true }));
      setAnalysis(prev => ({ ...prev, loading: true }));
      
      try {
        const weightResult = await fetchFitbitWeight(dateRange.fromDate, dateRange.toDate);
        setWeightData({ 
          loading: false, 
          data: weightResult.data, 
          error: null 
        });
        
        const analysisResult = await analyzeFitbitWeight(dateRange.fromDate, dateRange.toDate);
        setAnalysis({ 
          loading: false, 
          data: analysisResult.analysis, 
          error: null 
        });
      } catch (err) {
        setWeightData(prev => ({ loading: false, data: prev.data, error: 'Failed to refresh data' }));
        setAnalysis(prev => ({ loading: false, data: prev.data, error: 'Failed to refresh analysis' }));
      }
    }
  };
  
  // ChartJSのデータ形式に変換
  const getChartData = () => {
    if (!analysis.data || !analysis.data.chart_data) {
      return {
        labels: [],
        datasets: [
          {
            label: 'Weight',
            data: [],
            fill: false,
            backgroundColor: 'rgb(75, 192, 192)',
            borderColor: 'rgba(75, 192, 192, 0.8)',
          }
        ]
      };
    }
    
    const chartData = analysis.data.chart_data;
    return {
      labels: chartData.map(entry => entry.date),
      datasets: [
        {
          label: 'Weight (kg)',
          data: chartData.map(entry => entry.weight),
          fill: false,
          backgroundColor: 'rgb(75, 192, 192)',
          borderColor: 'rgba(75, 192, 192, 0.8)',
          tension: 0.1
        }
      ]
    };
  };
  
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Weight Trend',
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      }
    }
  };
  
  if (authStatus.loading) {
    return <p>Checking authentication...</p>;
  }
  
  return (
    <div>
      <h1>Fitbit Weight Dashboard</h1>
      
      <div className="card">
        <h2>Date Range</h2>
        <div className="date-range-selector">
          <div className="form-group">
            <label htmlFor="fromDate">From:</label>
            <input 
              type="date" 
              id="fromDate" 
              name="fromDate" 
              value={dateRange.fromDate} 
              onChange={handleDateChange} 
            />
          </div>
          <div className="form-group">
            <label htmlFor="toDate">To:</label>
            <input 
              type="date" 
              id="toDate" 
              name="toDate" 
              value={dateRange.toDate} 
              onChange={handleDateChange} 
              max={new Date().toISOString().split('T')[0]}  // 今日以降は選択不可
            />
          </div>
          <button className="btn" onClick={handleRefresh}>Refresh Data</button>
        </div>
      </div>
      
      {analysis.loading ? (
        <p>Loading analysis...</p>
      ) : analysis.error ? (
        <p className="error">{analysis.error}</p>
      ) : analysis.data ? (
        <div className="card">
          <h2>Weight Analysis</h2>
          <div className="summary-stats">
            <div className="stat-box">
              <h3>Starting Weight</h3>
              <p>{analysis.data.start_weight?.toFixed(1) || 'N/A'} kg</p>
            </div>
            <div className="stat-box">
              <h3>Current Weight</h3>
              <p>{analysis.data.end_weight?.toFixed(1) || 'N/A'} kg</p>
            </div>
            <div className="stat-box">
              <h3>Change</h3>
              <p className={analysis.data.change > 0 ? 'increase' : analysis.data.change < 0 ? 'decrease' : ''}>
                {analysis.data.change?.toFixed(1) || '0'} kg
              </p>
            </div>
            <div className="stat-box">
              <h3>Average</h3>
              <p>{analysis.data.avg_weight?.toFixed(1) || 'N/A'} kg</p>
            </div>
          </div>
          
          <div className="chart-container">
            <Line data={getChartData()} options={chartOptions} />
          </div>
        </div>
      ) : null}
      
      {weightData.loading ? (
        <p>Loading weight data...</p>
      ) : weightData.error ? (
        <p className="error">{weightData.error}</p>
      ) : weightData.data && weightData.data.length > 0 ? (
        <div className="card">
          <h2>Weight Records</h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Weight (kg)</th>
                  <th>BMI</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {weightData.data.map((entry) => (
                  <tr key={entry.id}>
                    <td>{entry.date}</td>
                    <td>{entry.time || 'N/A'}</td>
                    <td>{entry.weight.toFixed(1)}</td>
                    <td>{entry.bmi?.toFixed(1) || 'N/A'}</td>
                    <td>{entry.source || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="card">
          <p>No weight data available for the selected period.</p>
        </div>
      )}
    </div>
  );
};

export default FitbitDashboard;