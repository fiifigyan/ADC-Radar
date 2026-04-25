import { FaChartBar, FaCode, FaDatabase, FaGlobe, FaRobot, FaSearch } from 'react-icons/fa';
import '../styles/About.css';

const FEATURES = [
  { icon: <FaSearch />, title: 'Smart Scraping', desc: 'Automated scraping from Devex, Impactpool, UNDP, World Bank, and DevelopmentAid with anti-blocking measures.' },
  { icon: <FaRobot />,  title: 'AI Analysis',   desc: 'GPT-powered relevance scoring, confidence rating, and concise summaries for each opportunity.' },
  { icon: <FaChartBar />, title: 'Analytics',   desc: 'Real-time dashboards showing source distribution, priority breakdown, regional coverage, and skill trends.' },
  { icon: <FaDatabase />, title: 'Local + Notion', desc: 'All data is saved locally in JSON, with optional sync to a Notion database for team sharing.' },
  { icon: <FaGlobe />,  title: 'Africa Focus',  desc: 'Curated specifically for digital, data, and IT consultancy roles across the African continent.' },
  { icon: <FaCode />,   title: 'Open Source',   desc: 'Built with Flask + React. Contributions are welcome — fork, extend, and adapt it for your workflow.' },
];

const PLATFORMS = [
  { name: 'Devex',          color: '#EC4899', url: 'https://www.devex.com',            desc: 'Global development jobs' },
  { name: 'Impactpool',     color: '#6366F1', url: 'https://www.impactpool.org',        desc: 'International org careers' },
  { name: 'UNDP',           color: '#06B6D4', url: 'https://jobs.undp.org',             desc: 'UN Development Programme' },
  { name: 'World Bank',     color: '#3B82F6', url: 'https://worldbankgroup.csod.com',   desc: 'World Bank Group jobs' },
  { name: 'DevelopmentAid', color: '#8B5CF6', url: 'https://www.developmentaid.org',   desc: 'Aid sector opportunities' },
];

export default function About() {
  return (
    <div className="about-page">
      <div className="about-hero">
        <div className="about-radar-icon" aria-hidden="true">
          <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="40" cy="40" r="36" stroke="currentColor" strokeWidth="2" strokeDasharray="6 3" opacity="0.3" />
            <circle cx="40" cy="40" r="24" stroke="currentColor" strokeWidth="1.5" opacity="0.5" />
            <circle cx="40" cy="40" r="12" stroke="currentColor" strokeWidth="1" opacity="0.7" />
            <circle cx="40" cy="40" r="5"  fill="currentColor" />
            <line x1="40" y1="4"  x2="40" y2="20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <line x1="76" y1="40" x2="60" y2="40" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </div>
        <h1>About ADC Radar</h1>
        <p className="about-tagline">
          Illuminating Africa's digital consultancy opportunity landscape — automatically, intelligently, continuously.
        </p>
      </div>

      <div className="about-intro">
        <p>
          <strong>ADC Radar</strong> is an intelligence platform built for Africa-focused digital consultants
          and organisations. It continuously monitors the web for individual consultancy contracts,
          roster calls, and short-term expert positions — then uses AI to score, summarise, and prioritise
          every opportunity so your team can act fast.
        </p>
      </div>

      {/* Features */}
      <section className="about-section">
        <h2>Key Features</h2>
        <div className="feature-grid">
          {FEATURES.map(f => (
            <div key={f.title} className="feature-card">
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Platforms */}
      <section className="about-section">
        <h2>Monitored Platforms</h2>
        <div className="platform-grid">
          {PLATFORMS.map(p => (
            <a key={p.name} href={p.url} target="_blank" rel="noopener noreferrer"
              className="platform-card" style={{ '--plat-color': p.color }}>
              <div className="platform-dot" />
              <div>
                <strong>{p.name}</strong>
                <p>{p.desc}</p>
              </div>
            </a>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="about-section">
        <h2>How It Works</h2>
        <div className="flow-steps">
          {[
            { n: '01', t: 'Scrape', d: 'Scheduled or on-demand scraping from 5 major platforms using rotating user-agents and rate-limiting.' },
            { n: '02', t: 'Score',  d: 'OpenAI GPT analyses each opportunity and assigns a relevance score, confidence rating, and priority level.' },
            { n: '03', t: 'Review', d: 'Browse the Dashboard with advanced filters — by source, priority, relevance, deadline, and more.' },
            { n: '04', t: 'Share',  d: 'Sync the curated shortlist to Notion or receive weekly email digests with top opportunities.' },
          ].map(s => (
            <div key={s.n} className="flow-step">
              <span className="flow-num">{s.n}</span>
              <div>
                <h3>{s.t}</h3>
                <p>{s.d}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Tech stack */}
      <section className="about-section about-tech">
        <h2>Tech Stack</h2>
        <div className="tech-tags">
          {['Python 3.11+', 'Flask 3.0', 'BeautifulSoup 4', 'APScheduler', 'OpenAI GPT', 'React 19', 'Vite', 'Notion API', 'Docker'].map(t => (
            <span key={t} className="tech-tag">{t}</span>
          ))}
        </div>
      </section>
    </div>
  );
}
