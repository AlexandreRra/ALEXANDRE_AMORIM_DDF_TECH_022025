import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { fetchProductDistribution } from '../../services/productService';
import { ProductDistribution } from '../../models/product';
import 'chart.js/auto';
import './ProductDistributionChart.css';

const COLORS = ['#0c62d0', '#1984c5', '#22a7f0', '#00C8FF', '#76c68f'];

const ProductDistributionChart: React.FC = () => {
  const [data, setData] = useState<ProductDistribution[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const distribution = await fetchProductDistribution();
        setData(distribution);
      } catch (error) {
        console.error('Failed to load chart data:', error);
        setError(error instanceof Error ? error.message : 'Unknown error');
        setData(null);
      }
    };
    loadData();
  }, []);

  const chartData = {
    labels: Array.isArray(data) ? data.map(item => `Type ${item.product_type_id}`) : [],
    datasets: [
      {
        label: 'Product Count', 
        data: Array.isArray(data) ? data.map(item => item.count) : [],
        backgroundColor: COLORS[0],
        borderColor: COLORS[0],
        borderWidth: 1,
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
          text: 'Product Type ID',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Number of Products',
        },
        beginAtZero: true,
      },
    },
    plugins: {
      title: {
        display: true,
        text: 'Top 20 Product Distribution by Type',
      },
      legend: {
        display: true,
      },
    },
  };

  return (
    <div className="chart-container">
      {error ? (
        <p>{error}</p>
      ) : data ? (
        <div className="chart-wrapper">
          <Bar data={chartData} options={options} />
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default ProductDistributionChart;