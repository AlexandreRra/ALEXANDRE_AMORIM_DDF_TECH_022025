import React, { useEffect, useState } from 'react';
import { Chart } from 'react-chartjs-2';
import 'chart.js/auto';
import 'chartjs-chart-matrix';
import { Chart as ChartJS } from 'chart.js';
import { MatrixController, MatrixElement } from "chartjs-chart-matrix";
import { fetchDensityHeatmap } from '../../services/productService';
import './DensityHeatmapChart.css';

ChartJS.register(MatrixController, MatrixElement);

interface DensityHeatmap {
  length_bucket: number;
  product_type_id: number;
  count: number;
}

const DensityHeatmapChart: React.FC = () => {
  const [heatmap, setHeatmap] = useState<DensityHeatmap[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchDensityHeatmap();
        setHeatmap(data);
      } catch (error) {
        console.error('Failed to load density heatmap data:', error);
        setError(error instanceof Error ? error.message : 'Unknown error');
        setHeatmap(null);
      }
    };
    loadData();
  }, []);

  const chartData = {
    datasets: [
      {
        label: 'Density of Product Length by Type',
        data: heatmap?.map(item => ({
          x: item.length_bucket,
          y: item.product_type_id,
          v: item.count,
        })) || [],
        backgroundColor: (context: any) => {
          const value = context.dataset.data[context.dataIndex].v;
          const maxCount = Math.max(...(heatmap?.map(d => d.count) || [1]));
          const alpha = value / maxCount;
          return `rgba(12, 98, 208, ${alpha})`;
        },
        borderColor: 'rgba(12, 98, 208, 0.5)',
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
          text: 'Product Length Bucket',
          color: '#333333',
        },
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
        ticks: {
          stepSize: 1,
          color: '#333333',
        },
      },
    },
    plugins: {
      title: {
        display: true,
        text: 'Density Heatmap: Product Length vs Type',
        color: '#0c62d0',
      },
      legend: {
        display: false,
        labels: {
          color: '#333333',
        },
      },
    },
    type: 'matrix' as const,
  };

  return (
    <div className="chart-container">
      {error ? (
        <p>{error}</p>
      ) : heatmap ? (
        <div className="chart-wrapper">
          <Chart type="matrix" data={chartData} options={options} />
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default DensityHeatmapChart;