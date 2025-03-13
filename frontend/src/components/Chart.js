import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Chart = ({ data }) => {
  if (!data || data.length === 0) {
    return <p>No data available for chart.</p>;
  }

  // Group data by category
  const categories = [...new Set(data.map(item => item.category))];
  const chartData = {
    labels: categories,
    datasets: [
      {
        label: 'Total Value by Category',
        data: categories.map(category => {
          return data
            .filter(item => item.category === category)
            .reduce((sum, item) => sum + Number(item.value), 0);
        }),
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        borderColor: 'rgba(53, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Data by Category',
      },
    },
  };

  return (
    <div className="chart-container">
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default Chart;