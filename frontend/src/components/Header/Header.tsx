import React from 'react';
import { NavLink } from 'react-router-dom';
import './Header.css';

interface HeaderProps {
  onToggleTheme: () => void;
  isDarkMode: boolean;
}

const Header: React.FC<HeaderProps> = ({ onToggleTheme, isDarkMode }) => {
  const charts = [
    { name: 'Product Distribution by Type', path: '/charts/distribution' },
    { name: 'Product Length vs Type (Scatter)', path: '/charts/scatter' },
    { name: 'Empty Columns Distribution', path: '/charts/empty-columns' },
    { name: 'Temporal Trend of Products', path: '/charts/temporal-trend' },
    { name: 'Density Heatmap', path: '/charts/density-heatmap' }
  ];

  return (
    <header className="header">
      <nav>
        <ul className="nav-menu">
          {charts.map((chart, index) => (
            <li key={index} className="nav-item">
              <NavLink
                to={chart.path}
                className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
              >
                {chart.name}
              </NavLink>
            </li>
          ))}
          <li className="nav-item">
            <button onClick={onToggleTheme} className="theme-toggle">
              {isDarkMode ? 'Light Mode' : 'Dark Mode'}
            </button>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;