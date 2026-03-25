// frontend/src/components/Footer.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { FaTwitter, FaLinkedin, FaGithub, FaDiscord, FaEnvelope } from 'react-icons/fa';
import '../styles/Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-container">
          <div className="footer-main">
            <div className="footer-brand">
              <div className="footer-logo">
                <img src="/favicon.svg" alt="Dartex DC Radar Logo" />
                <h2>Dartex DC Radar</h2>
              </div>
              <p className="footer-tagline">
                Illuminating opportunities in the African digital landscape
              </p>
              <div className="footer-social">
                <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="Twitter">
                  <FaTwitter />
                </a>
                <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="LinkedIn">
                  <FaLinkedin />
                </a>
                <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="GitHub">
                  <FaGithub />
                </a>
              </div>
            </div>
            
            <div className="footer-links-container">
              <div className="footer-links-column">
                <h4>Navigation</h4>
                <ul className="footer-links">
                  <li><Link to="/home">Home</Link></li>
                  <li><Link to="/stats">Statistics</Link></li>
                  <li><Link to="/submit">Submit Data</Link></li>
                  <li><Link to="/about">About Us</Link></li>
                </ul>
              </div>
              
              <div className="footer-links-column">
                <h4>Resources</h4>
                <ul className="footer-links">
                  <li><Link to="/blog">Blog</Link></li>
                  <li><Link to="/case-studies">Case Studies</Link></li>
                  <li><Link to="/faq">FAQ</Link></li>
                  <li><Link to="/documentation">Documentation</Link></li>
                </ul>
              </div>
              
              <div className="footer-links-column">
                <h4>Legal</h4>
                <ul className="footer-links">
                  <li><Link to="/privacy">Privacy Policy</Link></li>
                  <li><Link to="/terms">Terms of Service</Link></li>
                  <li><Link to="/cookies">Cookie Policy</Link></li>
                  <li><Link to="/disclaimer">Disclaimer</Link></li>
                </ul>
              </div>
              
              <div className="footer-newsletter">
                <h4>Stay Updated</h4>
                <p>Subscribe to our newsletter for the latest updates and insights.</p>
                <form className="newsletter-form">
                  <input type="email" placeholder="Your email address" required />
                  <button type="submit">Subscribe</button>
                </form>
              </div>
            </div>
          </div>
          
          <div className="footer-divider"></div>
          
          <div className="footer-bottom">
            <p className="copyright">
              &copy; {currentYear} Dartex DC Radar. All rights reserved.
            </p>
            <div className="footer-badges">
              <span className="badge">
                <span className="dot"></span> Made with ❤️ in Africa
              </span>
              <span className="badge">
                <span className="dot"></span> Data-driven insights
              </span>
            </div>
            <a href="mailto:contact@dartexdc.com" className="footer-contact">
              <FaEnvelope /> Contact Us
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;