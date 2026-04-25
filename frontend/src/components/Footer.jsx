import { Link } from 'react-router-dom';
import { FaGithub, FaLinkedin, FaTwitter } from 'react-icons/fa';
import '../styles/Footer.css';

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <span className="footer-logo-name">ADC<span>Radar</span></span>
          <p>Illuminating Africa's digital consultancy landscape.</p>
        </div>

        <nav className="footer-nav" aria-label="Footer navigation">
          <Link to="/home">Dashboard</Link>
          <Link to="/stats">Stats</Link>
          <Link to="/scrape">Scrape</Link>
          <Link to="/analyze">Analyze</Link>
          <Link to="/submit">Submit</Link>
          <Link to="/about">About</Link>
        </nav>

        <div className="footer-social">
          <a href="https://twitter.com"  target="_blank" rel="noopener noreferrer" aria-label="Twitter"><FaTwitter /></a>
          <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><FaLinkedin /></a>
          <a href="https://github.com"   target="_blank" rel="noopener noreferrer" aria-label="GitHub"><FaGithub /></a>
        </div>
      </div>

      <div className="footer-bottom">
        <p>&copy; {year} ADC Radar &mdash; Africa Digital Consultancy</p>
        <p className="footer-made">Made with ♥ in Africa</p>
      </div>
    </footer>
  );
}
