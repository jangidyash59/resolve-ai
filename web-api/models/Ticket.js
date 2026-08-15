/**
 * Mongoose Schema for Support Tickets
 * Stores ticket data, AI-generated responses, and audit trail
 */

import mongoose from 'mongoose';

const orderItemSchema = new mongoose.Schema({
  name: { type: String, required: true },
  sku: { type: String, default: '' },
  category: { type: String, default: '' },
  price: { type: Number, required: true },
  quantity: { type: Number, default: 1 }
}, { _id: false });

const orderContextSchema = new mongoose.Schema({
  order_id: { type: String, required: true },
  order_date: { type: String, required: true },
  delivery_date: String,
  estimated_delivery: String,
  items: [orderItemSchema],
  total_amount: { type: Number, required: true },
  payment_method: { type: String, default: 'credit_card' },
  shipping_method: { type: String, default: 'standard' },
  shipping_address_country: { type: String, default: 'US' },
  shipping_address_state: String,
  seller_type: { type: String, default: 'direct' },
  seller_name: String
}, { _id: false });

const ticketSchema = new mongoose.Schema({
  // Ticket identification
  ticket_id: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  
  // Customer information
  customer_name: {
    type: String,
    required: true
  },
  customer_email: {
    type: String,
    required: true,
    lowercase: true,
    trim: true
  },
  customer_tier: {
    type: String,
    enum: ['bronze', 'silver', 'gold', 'platinum'],
    default: 'bronze'
  },
  
  // Ticket content
  ticket_text: {
    type: String,
    required: true
  },
  
  // Order information
  order_context: orderContextSchema,
  
  // AI Resolution data
  issue_type: String,
  priority: {
    type: String,
    enum: ['low', 'medium', 'high', 'urgent']
  },
  customer_response: String,
  internal_notes: String,
  actions_to_take: [String],
  citations: [String],
  
  // Status tracking
  status: {
    type: String,
    enum: ['pending', 'processing', 'resolved', 'escalated', 'failed'],
    default: 'pending',
    index: true
  },
  compliance_status: String,
  requires_escalation: {
    type: Boolean,
    default: false
  },
  escalation_reason: String,
  rewrite_count: {
    type: Number,
    default: 0
  },
  
  // Performance metrics
  processing_time_ms: Number,
  
  // Error tracking
  error_message: String,
  
  // Timestamps
  created_at: {
    type: Date,
    default: Date.now,
    index: true
  },
  updated_at: {
    type: Date,
    default: Date.now
  },
  resolved_at: Date
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Indexes for efficient queries
ticketSchema.index({ customer_email: 1, created_at: -1 });
ticketSchema.index({ status: 1, created_at: -1 });
ticketSchema.index({ requires_escalation: 1, status: 1 });
ticketSchema.index({ issue_type: 1 });

// Virtual for formatting date
ticketSchema.virtual('formatted_date').get(function() {
  return this.created_at.toISOString().split('T')[0];
});

// Method to mark ticket as resolved
ticketSchema.methods.markResolved = function() {
  this.status = this.requires_escalation ? 'escalated' : 'resolved';
  this.resolved_at = new Date();
  return this.save();
};

// Method to mark ticket as failed
ticketSchema.methods.markFailed = function(errorMessage) {
  this.status = 'failed';
  this.error_message = errorMessage;
  return this.save();
};

// Static method to get tickets by status
ticketSchema.statics.findByStatus = function(status) {
  return this.find({ status }).sort({ created_at: -1 });
};

// Static method to get escalated tickets
ticketSchema.statics.findEscalated = function() {
  return this.find({ requires_escalation: true }).sort({ created_at: -1 });
};

// Static method to get statistics
ticketSchema.statics.getStats = async function() {
  const total = await this.countDocuments();
  const resolved = await this.countDocuments({ status: 'resolved' });
  const escalated = await this.countDocuments({ requires_escalation: true });
  const pending = await this.countDocuments({ status: 'pending' });
  const avgProcessingTime = await this.aggregate([
    { $match: { processing_time_ms: { $exists: true } } },
    { $group: { _id: null, avgTime: { $avg: '$processing_time_ms' } } }
  ]);
  
  return {
    total,
    resolved,
    escalated,
    pending,
    resolution_rate: total > 0 ? ((resolved / total) * 100).toFixed(2) : 0,
    escalation_rate: total > 0 ? ((escalated / total) * 100).toFixed(2) : 0,
    avg_processing_time_ms: avgProcessingTime[0]?.avgTime || 0
  };
};

const Ticket = mongoose.model('Ticket', ticketSchema);

export default Ticket;
