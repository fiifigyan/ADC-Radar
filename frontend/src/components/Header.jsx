import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { FaTwitter, FaLinkedin, FaGithub, FaBars, FaTimes } from 'react-icons/fa';
import '../styles/Header.css';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    // Prevent scrolling when menu is open
    document.body.style.overflow = isMenuOpen ? 'auto' : 'hidden';
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
    document.body.style.overflow = 'auto';
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="logo-container">
          <img src="/favicon.svg" alt="Radar Logo" className="logo" />
          <h1 className="title">Dartex DC Radar</h1>
        </div>
        
        <button 
          className="mobile-menu-btn" 
          onClick={toggleMenu}
          aria-label="Toggle menu"
        >
          {isMenuOpen ? <FaTimes /> : <FaBars />}
        </button>
        
        <nav className={`nav-links ${isMenuOpen ? 'open' : ''}`}>
          <NavLink to="/home" className="nav-link" activeClassName="active" onClick={closeMenu}>Home</NavLink>
          <NavLink to="/stats" className="nav-link" activeClassName="active" onClick={closeMenu}>Stats</NavLink>
          <NavLink to="/submit" className="nav-link" activeClassName="active" onClick={closeMenu}>Submit</NavLink>
          <NavLink to="/about" className="nav-link" activeClassName="active" onClick={closeMenu}>About</NavLink>
          
          <div className="social-links">
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-icon">
              <FaTwitter />
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="social-icon">
              <FaLinkedin />
            </a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="social-icon">
              <FaGithub />
            </a>
          </div>
        </nav>
        
        {/* Overlay for mobile menu */}
        <div 
          className={`menu-overlay ${isMenuOpen ? 'open' : ''}`} 
          onClick={closeMenu}
        ></div>
      </div>
    </header>
  );
};

export default Header;