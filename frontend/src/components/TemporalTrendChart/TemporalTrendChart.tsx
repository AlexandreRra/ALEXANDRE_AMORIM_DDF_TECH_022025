import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { fetchTemporalTrend } from '../../services/productService';
import './TemporalTrendChart.css';
import { TemporalTrend } from '../../models/product';

const TemporalTrendChart: React.FC = () => {
  const [trend, setTrend] = useState<TemporalTrend[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchTemporalTrend();
        setTrend(data);
      } catch (error) {
        console.error('Failed to load temporal trend data:', error);
        setError(error instanceof Error ? error.message : 'Unknown error');
        setTrend(null);
      }
    };
    loadData();
  }, []);

  const chartData = {
    labels: trend?.map(item => item.product_type_id) || [],
    datasets: [
      {
        label: 'Number of Products Over Time',
        data: trend?.map(item => item.count) || [],
        fill: false,
        borderColor: '#0c62d0',
        tension: 0.1,
      },
    ],
  };

  const options = {
    maintainAspectRatio: false,
    responsive: true,
    scales: {
      x: {
        title: {
          display: true,
          text: 'Time Index (Sorted Product ID)',
          color: '#333333',
        },
        ticks: {
          color: '#333333',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Number of Products',
          color: '#333333',
        },
        beginAtZero: true,
        ticks: {
          color: '#333333',
        },
      },
    },
    plugins: {
      title: {
        display: true,
        text: 'Temporal Trend of Products',
        color: '#0c62d0',
      },
      legend: {
        display: false,
        labels: {
          color: '#333333',
        },
      },
    },
  };

  return (
    <div className="chart-container">
      {error ? (
        <p>{error}</p>
      ) : trend ? (
        <div className="chart-wrapper">
          <Line data={chartData} options={options} />
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default TemporalTrendChart;