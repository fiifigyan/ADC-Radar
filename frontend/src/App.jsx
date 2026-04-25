import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom';
import './App.css';
import { NotificationProvider } from './contexts/NotificationContext';
import { ThemeProvider } from './contexts/ThemeContext';
import Footer from './components/Footer';
import Header from './components/Header';
import About from './pages/About';
import Analyze from './pages/Analyze';
import Dashboard from './pages/Dashboard';
import Scrape from './pages/Scrape';
import Stats from './pages/Stats';
import Submit from './pages/Submit';

export default function App() {
  return (
    <ThemeProvider>
      <NotificationProvider>
        <Router>
          <div className="app">
            <Header />
            <main className="main-content">
              <Routes>
                <Route path="/"        element={<Navigate to="/home" replace />} />
                <Route path="/home"    element={<Dashboard />} />
                <Route path="/stats"   element={<Stats />} />
                <Route path="/scrape"  element={<Scrape />} />
                <Route path="/analyze" element={<Analyze />} />
                <Route path="/submit"  element={<Submit />} />
                <Route path="/about"   element={<About />} />
                <Route path="*"        element={<Navigate to="/home" replace />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </Router>
      </NotificationProvider>
    </ThemeProvider>
  );
}
