import React, { useEffect, useState } from 'react';
import { Scatter } from 'react-chartjs-2';
import { fetchScatterDistribution } from '../../services/productService';
import { ProductScatter } from '../../models/product';
import 'chart.js/auto';
import './ScatterDistributionChart.css';

const COLORS = ['#FF6384', '#0c62d0', '#00C8FF', '#6f42c1', '#FFCE56', '#76c68f']; 

const ScatterDistributionChart: React.FC = () => {
  const [data, setData] = useState<ProductScatter[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const distribution = await fetchScatterDistribution();
        setData(distribution);
      } catch (error) {
        console.error('Failed to load scatter data:', error);
        setError(error instanceof Error ? error.message : 'Unknown error');
        setData(null);
      }
    };
    loadData();
  }, []);

  const chartData = {
    datasets: [
      {
        label: 'Product Length vs Type',
        data: Array.isArray(data) ? data.map(item => ({
          x: item.product_length, 
          y: item.product_type_id, 
        })) : [],
        backgroundColor: Array.isArray(data) ? data.map(item => 
          COLORS[item.product_type_id % COLORS.length] 
        ) : [],
        pointRadius: 5, 
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
          text: 'Product Length',
          color: '#333333', 
        },
        beginAtZero: true,
        ticks: {
          color: '#333333', 
        },
      },
      y: {
        title: {
          display: true,
          text: 'Product Type ID',
          color: '#333333', 
        },
        beginAtZero: true,
        ticks: {
          stepSize: 1, 
          color: '#333333', 
        },
      },
    },
    plugins: {
      title: {
        display: true,
        text: 'Scatter Plot: Relationship Between Product Length and Type',
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
      ) : data ? (
        <div className="chart-wrapper">
          <Scatter data={chartData} options={options} />
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default ScatterDistributionChart;