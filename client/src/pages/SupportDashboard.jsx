import { useState, useEffect } from 'react'
import { RefreshCw, TrendingUp, AlertTriangle, CheckCircle, Clock, Search, Filter } from 'lucide-react'
import axios from 'axios'
import { formatDistanceToNow } from 'date-fns'
import './SupportDashboard.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

function SupportDashboard() {
  const [tickets, setTickets] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, resolved, escalated, pending
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [ticketsRes, statsRes] = await Promise.all([
        axios.get(`${API_URL}/api/tickets`),
        axios.get(`${API_URL}/api/stats/summary`)
      ])
      
      setTickets(ticketsRes.data.tickets || [])
      setStats(statsRes.data.stats || {})
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredTickets = tickets.filter(ticket => {
    // Apply status filter
    if (filter === 'resolved' && ticket.status !== 'resolved') return false
    if (filter === 'escalated' && !ticket.requires_escalation) return false
    if (filter === 'pending' && ticket.status !== 'pending' && ticket.status !== 'processing') return false
    
    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      return (
        ticket.ticket_id.toLowerCase().includes(query) ||
        ticket.customer_name.toLowerCase().includes(query) ||
        ticket.customer_email.toLowerCase().includes(query) ||
        ticket.ticket_text.toLowerCase().includes(query)
      )
    }
    
    return true
  })

  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved': return 'success'
      case 'escalated': return 'error'
      case 'pending': return 'warning'
      case 'processing': return 'info'
      case 'failed': return 'error'
      default: return 'info'
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'error'
      case 'high': return 'error'
      case 'medium': return 'warning'
      case 'low': return 'success'
      default: return 'info'
    }
  }

  return (
    <div className="container">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Support Dashboard</h1>
          <p className="dashboard-subtitle">Monitor and manage AI-resolved support tickets</p>
        </div>
        <button className="btn btn-secondary" onClick={fetchData} disabled={loading}>
          <RefreshCw size={18} className={loading ? 'spinning' : ''} />
          Refresh
        </button>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'rgba(124, 58, 237, 0.15)', color: 'var(--primary-light)' }}>
              <TrendingUp size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.total || 0}</div>
              <div className="stat-label">Total Tickets</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--success)' }}>
              <CheckCircle size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.resolved || 0}</div>
              <div className="stat-label">Resolved</div>
              <div className="stat-badge badge-success">{stats.resolution_rate}% rate</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'rgba(239, 68, 68, 0.15)', color: 'var(--error)' }}>
              <AlertTriangle size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.escalated || 0}</div>
              <div className="stat-label">Escalated</div>
              <div className="stat-badge badge-error">{stats.escalation_rate}% rate</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'rgba(6, 182, 212, 0.15)', color: 'var(--secondary)' }}>
              <Clock size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{(stats.avg_processing_time_ms / 1000).toFixed(1)}s</div>
              <div className="stat-label">Avg Processing Time</div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="filters-bar glass-card">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search tickets by ID, customer, or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-buttons">
          <Filter size={18} />
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            className={`filter-btn ${filter === 'resolved' ? 'active' : ''}`}
            onClick={() => setFilter('resolved')}
          >
            Resolved
          </button>
          <button
            className={`filter-btn ${filter === 'escalated' ? 'active' : ''}`}
            onClick={() => setFilter('escalated')}
          >
            Escalated
          </button>
          <button
            className={`filter-btn ${filter === 'pending' ? 'active' : ''}`}
            onClick={() => setFilter('pending')}
          >
            Pending
          </button>
        </div>
      </div>

      {/* Tickets List */}
      {loading ? (
        <div className="loading-container">
          <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '4px' }} />
          <p style={{ marginTop: '16px', color: 'rgba(255,255,255,0.5)' }}>Loading tickets...</p>
        </div>
      ) : filteredTickets.length === 0 ? (
        <div className="empty-state glass-card">
          <AlertTriangle size={48} style={{ opacity: 0.3 }} />
          <h3>No tickets found</h3>
          <p>Try adjusting your filters or search query</p>
        </div>
      ) : (
        <div className="tickets-grid">
          {filteredTickets.map(ticket => (
            <div key={ticket._id} className="ticket-card glass-card">
              <div className="ticket-header">
                <div>
                  <div className="ticket-id">{ticket.ticket_id}</div>
                  <div className="ticket-customer">{ticket.customer_name}</div>
                  <div className="ticket-time">
                    {ticket.created_at && formatDistanceToNow(new Date(ticket.created_at), { addSuffix: true })}
                  </div>
                </div>
                <div className="ticket-badges">
                  <span className={`badge badge-${getStatusColor(ticket.status)}`}>
                    {ticket.status}
                  </span>
                  {ticket.priority && (
                    <span className={`badge badge-${getPriorityColor(ticket.priority)}`}>
                      {ticket.priority}
                    </span>
                  )}
                </div>
              </div>

              <div className="ticket-content">
                <div className="ticket-issue">
                  <strong>Issue:</strong> {ticket.ticket_text.substring(0, 150)}
                  {ticket.ticket_text.length > 150 ? '...' : ''}
                </div>

                {ticket.issue_type && (
                  <div className="ticket-meta">
                    <span className="badge badge-info">{ticket.issue_type}</span>
                    {ticket.order_context?.order_id && (
                      <span className="ticket-order">Order: {ticket.order_context.order_id}</span>
                    )}
                  </div>
                )}

                {ticket.requires_escalation && (
                  <div className="ticket-alert">
                    <AlertTriangle size={16} />
                    <span>{ticket.escalation_reason}</span>
                  </div>
                )}

                {ticket.customer_response && (
                  <div className="ticket-response">
                    <div className="response-label">AI Response:</div>
                    <div className="response-preview">
                      {ticket.customer_response.substring(0, 200)}
                      {ticket.customer_response.length > 200 ? '...' : ''}
                    </div>
                  </div>
                )}

                {ticket.citations && ticket.citations.length > 0 && (
                  <div className="ticket-citations">
                    <span className="citations-label">📎 {ticket.citations.length} Citations</span>
                    <div className="citations-preview">
                      {ticket.citations.slice(0, 2).map((citation, idx) => (
                        <span key={idx} className="citation-mini">{citation}</span>
                      ))}
                      {ticket.citations.length > 2 && <span className="citation-mini">+{ticket.citations.length - 2} more</span>}
                    </div>
                  </div>
                )}

                {ticket.processing_time_ms && (
                  <div className="ticket-footer">
                    <Clock size={14} />
                    <span>Processed in {(ticket.processing_time_ms / 1000).toFixed(1)}s</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SupportDashboard
