import { useState } from 'react'
import { Send, Loader2, CheckCircle, AlertTriangle, FileText } from 'lucide-react'
import axios from 'axios'
import './CustomerTicket.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

function CustomerTicket() {
  const [formData, setFormData] = useState({
    customer_name: 'Arjun Sharma',
    customer_email: 'arjun.sharma@example.com',
    customer_tier: 'silver',
    ticket_text: 'Mera order kal aaya lekin item damaged thi. Package bhi dented tha, shipping mein damage laga. Mujhe full refund chahiye.',
    // Order context
    has_order: true,
    order_id: 'ORD-2026-99001',
    order_date: '2026-03-25',
    delivery_date: '2026-03-27',
    item_name: 'Wireless Bluetooth Speaker',
    item_price: 149.99,
    total_amount: 149.99,
    payment_method: 'credit_card',
    shipping_method: 'standard'
  })

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const ticket_id = `TKT-${Date.now()}`
      
      const payload = {
        ticket_id,
        customer_name: formData.customer_name,
        customer_email: formData.customer_email,
        customer_tier: formData.customer_tier,
        ticket_text: formData.ticket_text,
        order_context: formData.has_order ? {
          order_id: formData.order_id,
          order_date: formData.order_date,
          delivery_date: formData.delivery_date || null,
          items: [{
            name: formData.item_name,
            price: parseFloat(formData.item_price),
            category: 'electronics',
            quantity: 1
          }],
          total_amount: parseFloat(formData.total_amount),
          payment_method: formData.payment_method,
          shipping_method: formData.shipping_method,
          shipping_address_country: 'IN',
          seller_type: 'direct'
        } : null
      }

      const response = await axios.post(`${API_URL}/api/tickets`, payload, {
        timeout: 90000
      })

      setResult(response.data.ticket)
    } catch (err) {
      console.error('Error submitting ticket:', err)
      setError(err.response?.data?.message || err.message || 'Failed to submit ticket')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="hero">
        <p className="hero-eyebrow">⚡ AI-Powered Support</p>
        <h1 className="hero-title">Submit Support Ticket</h1>
        <p className="hero-subtitle">
          Our AI agents will analyze your issue, search relevant policies, and provide an instant resolution.
        </p>
        <div className="hero-tags">
          <span className="badge badge-primary">4 AI Agents</span>
          <span className="badge badge-info">FAISS Vector DB</span>
          <span className="badge badge-success">Zero Hallucinations</span>
          <span className="badge badge-warning">100% Citations</span>
        </div>
      </div>

      {error && (
        <div className="alert alert-error fade-in">
          <AlertTriangle size={20} />
          <div>
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      {result && (
        <div className="result-panel fade-in">
          <div className="result-header">
            <div className="result-title">
              <CheckCircle size={28} className="result-icon" />
              <div>
                <h2>Ticket Resolved</h2>
                <p>Ticket ID: <strong>{result.ticket_id}</strong></p>
              </div>
            </div>
            
            <div className="result-meta">
              <div className="meta-item">
                <span className="meta-label">Issue Type</span>
                <span className={`badge badge-info`}>{result.issue_type}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Priority</span>
                <span className={`badge badge-${result.priority === 'urgent' || result.priority === 'high' ? 'error' : 'warning'}`}>
                  {result.priority}
                </span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Status</span>
                <span className={`badge ${result.requires_escalation ? 'badge-error' : 'badge-success'}`}>
                  {result.status}
                </span>
              </div>
              {result.processing_time_ms && (
                <div className="meta-item">
                  <span className="meta-label">Processing Time</span>
                  <span className="badge badge-primary">{(result.processing_time_ms / 1000).toFixed(1)}s</span>
                </div>
              )}
            </div>
          </div>

          {result.requires_escalation && (
            <div className="alert alert-warning">
              <AlertTriangle size={20} />
              <div>
                <strong>Escalation Required:</strong> {result.escalation_reason}
              </div>
            </div>
          )}

          <div className="result-section">
            <h3>
              <FileText size={18} />
              Customer Response
            </h3>
            <div className="response-text">
              {result.customer_response}
            </div>
          </div>

          {result.citations && result.citations.length > 0 && (
            <div className="result-section">
              <h3>📎 Policy Citations</h3>
              <div className="citations">
                {result.citations.map((citation, idx) => (
                  <span key={idx} className="citation-badge">
                    {citation}
                  </span>
                ))}
              </div>
            </div>
          )}

          {result.actions_to_take && result.actions_to_take.length > 0 && (
            <div className="result-section">
              <h3>✓ Actions Required</h3>
              <ul className="actions-list">
                {result.actions_to_take.map((action, idx) => (
                  <li key={idx}>{action}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="ticket-form-card glass-card">
        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <h3 className="section-title">Customer Information</h3>
            <div className="form-grid">
              <div className="form-group">
                <label className="label">Customer Name</label>
                <input
                  type="text"
                  name="customer_name"
                  value={formData.customer_name}
                  onChange={handleChange}
                  className="input"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="label">Email Address</label>
                <input
                  type="email"
                  name="customer_email"
                  value={formData.customer_email}
                  onChange={handleChange}
                  className="input"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="label">Loyalty Tier</label>
                <select
                  name="customer_tier"
                  value={formData.customer_tier}
                  onChange={handleChange}
                  className="select"
                >
                  <option value="bronze">🥉 Bronze</option>
                  <option value="silver">🥈 Silver</option>
                  <option value="gold">🥇 Gold</option>
                  <option value="platinum">💎 Platinum</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3 className="section-title">Issue Description</h3>
            <div className="form-group">
              <label className="label">Describe Your Issue</label>
              <textarea
                name="ticket_text"
                value={formData.ticket_text}
                onChange={handleChange}
                className="textarea"
                placeholder="Describe your issue in detail..."
                required
              />
            </div>
          </div>

          <div className="form-section">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="has_order"
                checked={formData.has_order}
                onChange={handleChange}
              />
              <span>Include Order Details</span>
            </label>

            {formData.has_order && (
              <div className="form-grid" style={{ marginTop: '16px' }}>
                <div className="form-group">
                  <label className="label">Order ID</label>
                  <input
                    type="text"
                    name="order_id"
                    value={formData.order_id}
                    onChange={handleChange}
                    className="input"
                  />
                </div>
                
                <div className="form-group">
                  <label className="label">Order Date</label>
                  <input
                    type="date"
                    name="order_date"
                    value={formData.order_date}
                    onChange={handleChange}
                    className="input"
                  />
                </div>
                
                <div className="form-group">
                  <label className="label">Delivery Date</label>
                  <input
                    type="date"
                    name="delivery_date"
                    value={formData.delivery_date}
                    onChange={handleChange}
                    className="input"
                  />
                </div>
                
                <div className="form-group">
                  <label className="label">Item Name</label>
                  <input
                    type="text"
                    name="item_name"
                    value={formData.item_name}
                    onChange={handleChange}
                    className="input"
                  />
                </div>
                
                <div className="form-group">
                  <label className="label">Item Price ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    name="item_price"
                    value={formData.item_price}
                    onChange={handleChange}
                    className="input"
                  />
                </div>
                
                <div className="form-group">
                  <label className="label">Payment Method</label>
                  <select
                    name="payment_method"
                    value={formData.payment_method}
                    onChange={handleChange}
                    className="select"
                  >
                    <option value="credit_card">Credit Card</option>
                    <option value="upi">UPI</option>
                    <option value="cash_on_delivery">Cash on Delivery</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', marginTop: '24px' }}>
            {loading ? (
              <>
                <div className="spinner" />
                Processing Ticket...
              </>
            ) : (
              <>
                <Send size={18} />
                Submit Ticket
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

export default CustomerTicket
