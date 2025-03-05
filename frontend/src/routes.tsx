import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App';
import ProductDistributionChart from './components/ProductDistributionChart/ProductDistributionChart';

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/charts/distribution', element: <ProductDistributionChart /> },
]);

export const Routes: React.FC = () => <RouterProvider router={router} />;