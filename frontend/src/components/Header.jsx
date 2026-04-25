import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { FaBars, FaGithub, FaLinkedin, FaMoon, FaSun, FaTimes, FaTwitter } from 'react-icons/fa';
import { useTheme } from '../contexts/ThemeContext';
import '../styles/Header.css';

const NAV_LINKS = [
  { to: '/home',    label: 'Dashboard' },
  { to: '/stats',   label: 'Stats' },
  { to: '/scrape',  label: 'Scrape' },
  { to: '/analyze', label: 'Analyze' },
  { to: '/submit',  label: 'Submit' },
  { to: '/about',   label: 'About' },
];

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { isDark, toggleTheme } = useTheme();

  const closeMenu = () => {
    setMenuOpen(false);
    document.body.style.overflow = '';
  };

  const toggleMenu = () => {
    const next = !menuOpen;
    setMenuOpen(next);
    document.body.style.overflow = next ? 'hidden' : '';
  };

  const navLinkClass = ({ isActive }) =>
    `nav-link${isActive ? ' nav-link--active' : ''}`;

  return (
    <header className="header">
      <div className="header-inner">
        {/* Brand */}
        <NavLink to="/home" className="brand" onClick={closeMenu} aria-label="ADC Radar home">
          <div className="brand-icon" aria-hidden="true">
            <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="2" strokeDasharray="4 2" opacity="0.4" />
              <circle cx="16" cy="16" r="9"  stroke="currentColor" strokeWidth="1.5" opacity="0.6" />
              <circle cx="16" cy="16" r="4"  fill="currentColor" />
              <line x1="16" y1="2" x2="16" y2="8"   stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              <line x1="30" y1="16" x2="24" y2="16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
          <span className="brand-name">ADC<span className="brand-accent">Radar</span></span>
        </NavLink>

        {/* Desktop nav */}
        <nav className="nav-desktop" aria-label="Main navigation">
          {NAV_LINKS.map(({ to, label }) => (
            <NavLink key={to} to={to} className={navLinkClass} end={to === '/home'}>
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Controls */}
        <div className="header-controls">
          <button
            className="icon-btn theme-btn"
            onClick={toggleTheme}
            aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
            title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
          >
            {isDark ? <FaSun /> : <FaMoon />}
          </button>

          <div className="social-row" aria-label="Social links">
            <a href="https://twitter.com"  target="_blank" rel="noopener noreferrer" className="icon-btn" aria-label="Twitter"><FaTwitter /></a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="icon-btn" aria-label="LinkedIn"><FaLinkedin /></a>
            <a href="https://github.com"   target="_blank" rel="noopener noreferrer" className="icon-btn" aria-label="GitHub"><FaGithub /></a>
          </div>

          <button
            className="icon-btn mobile-toggle"
            onClick={toggleMenu}
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={menuOpen}
          >
            {menuOpen ? <FaTimes /> : <FaBars />}
          </button>
        </div>
      </div>

      {/* Mobile drawer */}
      <div className={`mobile-nav${menuOpen ? ' mobile-nav--open' : ''}`} aria-hidden={!menuOpen}>
        <nav aria-label="Mobile navigation">
          {NAV_LINKS.map(({ to, label }) => (
            <NavLink key={to} to={to} className={navLinkClass} onClick={closeMenu} end={to === '/home'}>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="mobile-divider" />
        <div className="mobile-social">
          <a href="https://twitter.com"  target="_blank" rel="noopener noreferrer" className="icon-btn"><FaTwitter /></a>
          <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="icon-btn"><FaLinkedin /></a>
          <a href="https://github.com"   target="_blank" rel="noopener noreferrer" className="icon-btn"><FaGithub /></a>
        </div>
      </div>

      {menuOpen && <div className="nav-overlay" onClick={closeMenu} aria-hidden="true" />}
    </header>
  );
}
