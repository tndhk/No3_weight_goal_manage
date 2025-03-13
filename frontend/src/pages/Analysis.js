import React, { useState, useEffect } from 'react';
import { fetchAnalyticsData } from '../services/api';
import Chart from '../components/Chart';

const Analysis = () => {
  const [analyticsData, setAnalyticsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterCategory, setFilterCategory] = useState('all');

  useEffect(() => {
    const getAnalyticsData = async () => {
      try {
        setLoading(true);
        const result = await fetchAnalyticsData();
        setAnalyticsData(result);
        setError(null);
      } catch (err) {
        setError('Failed to fetch analytics data. Please try again later.');
        console.error('Error fetching analytics data:', err);
      } finally {
        setLoading(false);
      }
    };

    getAnalyticsData();
  }, []);

  const filteredData = filterCategory === 'all'
    ? analyticsData
    : analyticsData.filter(item => item.category === filterCategory);

  const categories = ['all', ...new Set(analyticsData.map(item => item.category))];

  return (
    <div>
      <h1>Data Analysis</h1>
      
      <div className="card">
        <h2>Analytics Overview</h2>
        
        {loading ? (
          <p>Loading analytics data...</p>
        ) : error ? (
          <p className="error">{error}</p>
        ) : (
          <>
            <div className="filter-container">
              <label htmlFor="category-filter">Filter by Category:</label>
              <select
                id="category-filter"
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
              >
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category === 'all' ? 'All Categories' : category}
                  </option>
                ))}
              </select>
            </div>
            
            <Chart data={filteredData} />
            
            <div className="analytics-summary">
              <h3>Summary Statistics</h3>
              <p>Total Items: {filteredData.length}</p>
              <p>Average Value: {
                filteredData.length > 0
                  ? (filteredData.reduce((sum, item) => sum + Number(item.value), 0) / filteredData.length).toFixed(2)
                  : 0
              }</p>
              <p>Maximum Value: {
                filteredData.length > 0
                  ? Math.max(...filteredData.map(item => Number(item.value)))
                  : 0
              }</p>
              <p>Minimum Value: {
                filteredData.length > 0
                  ? Math.min(...filteredData.map(item => Number(item.value)))
                  : 0
              }</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Analysis;