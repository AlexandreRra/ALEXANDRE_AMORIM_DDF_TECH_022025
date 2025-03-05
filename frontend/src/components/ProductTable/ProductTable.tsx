import React from 'react';
import './ProductTable.css';
import { PaginatedProducts } from '../../models/product';

interface ProductTableProps {
  products: PaginatedProducts;
  page: number;
  pageSize: number;
  onPageChange: (newPage: number) => void;
  onReturnToChart: () => void;
}

const ProductTable: React.FC<ProductTableProps> = ({ products, page, pageSize, onPageChange, onReturnToChart }) => {
  return (
    <div className="table-container">
      <div className="navigation-controls">
        <button onClick={onReturnToChart} className="return-button">
          Return to Pie Chart
        </button>
      </div>
      <h3>Products with {products.data[0].empty_cols === 'no_empty_data' ? 'No Empty Data' : `Empty ${products.data[0].empty_cols}`}</h3>
      <table className="products-table">
        <thead>
          <tr>
            <th>Product ID</th>
            <th>Title</th>
            <th>Bullet Points</th>
            <th>Description</th>
            <th>Product Type ID</th>
            <th>Product Length</th>
            <th>Empty Columns</th>
          </tr>
        </thead>
        <tbody>
          {products.data.map(product => (
            <tr key={product.product_id}>
              <td>{product.product_id}</td>
              <td>{product.title || 'N/A'}</td>
              <td>{product.bullet_points || 'N/A'}</td>
              <td>{product.description || 'N/A'}</td>
              <td>{product.product_type_id || 'N/A'}</td>
              <td>{product.product_length || 'N/A'}</td>
              <td>{product.empty_cols || 'no_empty_data'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="pagination">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
        >
          Previous
        </button>
        <span> Page {page} of {Math.ceil(products.total / pageSize)}</span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page * pageSize >= products.total}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default ProductTable;