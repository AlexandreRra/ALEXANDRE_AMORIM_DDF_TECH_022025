import React, { useState } from 'react';
import { Outlet, Route, Routes } from 'react-router-dom';
import './App.css';
import Header from './components/Header/Header';
import ProductDistributionChart from './components/ProductDistributionChart/ProductDistributionChart';
import ScatterDistributionChart from './components/ScatterDistributionChart/ScatterDistributionChart';
import EmptyColumnsChart from './components/EmptyColumnsChart/EmptyColumnsChart';
import TemporalTrendChart from './components/TemporalTrendChart/TemporalTrendChart';
import DensityHeatmapChart from './components/DensityHeatmapChart/DensityHeatmapChart';

interface AppLayoutProps {
  onToggleTheme: () => void;
  isDarkMode: boolean;
}

const AppLayout: React.FC<AppLayoutProps> = ({ onToggleTheme, isDarkMode }) => (
  <div className={`app-container ${isDarkMode ? 'dark-mode' : 'light-mode'}`}>
    <Header onToggleTheme={onToggleTheme} isDarkMode={isDarkMode} />
    <main className="main-content">
      <Outlet />
    </main>
  </div>
);

const App: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const handleToggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  return (
    <Routes>
      <Route path="/" element={<AppLayout onToggleTheme={handleToggleTheme} isDarkMode={isDarkMode} />}>
        <Route path="/charts/distribution" element={<ProductDistributionChart />} />
        <Route path="/charts/scatter" element={<ScatterDistributionChart />} />
        <Route path="/charts/empty-columns" element={<EmptyColumnsChart />} />
        <Route path="/charts/temporal-trend" element={<TemporalTrendChart />} />
        <Route path="/charts/density-heatmap" element={<DensityHeatmapChart />} />
      </Route>
    </Routes>
  );
};

export default App;