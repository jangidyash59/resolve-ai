import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Zap, TicketIcon, LayoutDashboard } from 'lucide-react'
import CustomerTicket from './pages/CustomerTicket'
import SupportDashboard from './pages/SupportDashboard'
import './App.css'

function Navigation() {
  const location = useLocation()
  
  return (
    <nav className="nav">
      <div className="container nav-container">
        <Link to="/" className="logo">
          <Zap size={28} />
          <span>ResolveAI</span>
        </Link>
        
        <div className="nav-links">
          <Link 
            to="/" 
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            <TicketIcon size={18} />
            New Ticket
          </Link>
          <Link 
            to="/dashboard" 
            className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
          >
            <LayoutDashboard size={18} />
            Dashboard
          </Link>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<CustomerTicket />} />
            <Route path="/dashboard" element={<SupportDashboard />} />
          </Routes>
        </main>
        
        <footer className="footer">
          <div className="container">
            <p>
              <strong>ResolveAI</strong> — MERN + FastAPI Microservices Architecture
              <span style={{ margin: '0 12px', opacity: 0.3 }}>•</span>
              4-Agent RAG Pipeline with FAISS Vector Search
            </p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
