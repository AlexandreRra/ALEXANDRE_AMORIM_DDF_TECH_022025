import React, { useEffect, useState } from 'react';
import { Pie } from 'react-chartjs-2';
import { fetchEmptyColumnsDistribution, fetchProductsByEmpty } from '../../services/productService';
import { EmptyColumnDistribution, PaginatedProducts } from '../../models/product';
import 'chart.js/auto';
import './EmptyColumnsChart.css';
import ProductTable from '../ProductTable/ProductTable';

const COLORS = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];

const EmptyColumnsChart: React.FC = () => {
  const [distribution, setDistribution] = useState<EmptyColumnDistribution[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<'chart' | 'table'>('chart');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [products, setProducts] = useState<PaginatedProducts | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchEmptyColumnsDistribution();
        setDistribution(data);
      } catch (error) {
        console.error('Failed to load empty columns data:', error);
        setError(error instanceof Error ? error.message : 'Unknown error');
        setDistribution(null);
      }
    };
    loadData();
  }, []);

  const handlePieClick = async (event: any, elements: any[]) => {
    if (elements.length > 0) {
      const index = elements[0].index;
      const category = distribution![index].category;
      setSelectedCategory(category);
      setView('table');
      setPage(1);
      try {
        const productData = await fetchProductsByEmpty(category, page, pageSize);
        setProducts(productData);
      } catch (error) {
        console.error('Failed to load products:', error);
        setError(error instanceof Error ? error.message : 'Unknown error');
        setProducts(null);
      }
    }
  };

  const chartData = {
    labels: distribution?.map(item => item.category) || [],
    datasets: [
      {
        data: distribution?.map(item => item.count) || [],
        backgroundColor: distribution?.map((_, i) => COLORS[i % COLORS.length]) || [],
        hoverBackgroundColor: distribution?.map((_, i) => COLORS[i % COLORS.length]) || [],
      },
    ],
  };

  const total = distribution?.reduce((sum, item) => sum + item.count, 0) || 0;
  const options = {
    maintainAspectRatio: false,
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Percentage of Empty Columns in Products',
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.label || '';
            const value = context.raw as number;
            const percentage = ((value / total) * 100).toFixed(2);
            return `${label}: ${value} (${percentage}%)`;
          },
        },
      },
      legend: {
        position: 'top' as const,
      },
    },
    onClick: handlePieClick,
  };

  const handlePageChange = (newPage: number) => {
    if (selectedCategory && view === 'table') {
      fetchProductsByEmpty(selectedCategory, newPage, pageSize)
        .then(productData => {
          setProducts(productData);
          setPage(newPage);
        })
        .catch(error => {
          console.error('Failed to load products:', error);
          setError(error instanceof Error ? error.message : 'Unknown error');
        });
    }
  };

  const handleReturnToChart = () => {
    setView('chart');
    setSelectedCategory(null);
    setProducts(null);
    setPage(1);
  };

  return (
    <div className="chart-container">
      {error ? (
        <p>{error}</p>
      ) : (
        <div className="chart-wrapper">
          {view === 'chart' ? (
            <Pie data={chartData} options={options} />
          ) : (
            selectedCategory && products && (
              <ProductTable
                products={products}
                page={page}
                pageSize={pageSize}
                onPageChange={handlePageChange}
                onReturnToChart={handleReturnToChart}
              />
            )
          )}
        </div>
      )}
    </div>
  );
};

export default EmptyColumnsChart;