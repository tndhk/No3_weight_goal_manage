import React, { useState, useEffect } from 'react';
import { fetchData } from '../services/api';
import DataTable from '../components/DataTable';
import Chart from '../components/Chart';

const Dashboard = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getData = async () => {
      try {
        setLoading(true);
        const result = await fetchData();
        setData(result);
        setError(null);
      } catch (err) {
        setError('Failed to fetch data. Please try again later.');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    getData();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      
      <div className="card">
        <h2>Data Overview</h2>
        {loading ? (
          <p>Loading data...</p>
        ) : error ? (
          <p className="error">{error}</p>
        ) : (
          <>
            <Chart data={data} />
            <DataTable data={data} />
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;