import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';
import Stats from './pages/Stats';
import Submit from './pages/Submit';
import About from './pages/About';

function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <main>
          <Routes>
            <Route path="/home" element={<Dashboard />} />
            <Route path="/stats" element={<Stats />} />
            <Route path="/submit" element={<Submit />} />
            <Route path="/about" element={<About />} />

            {/* Redirect to the default route */}
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
