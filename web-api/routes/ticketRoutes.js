/**
 * Ticket Routes
 * Handles ticket CRUD operations and proxies AI resolution to FastAPI service
 */

import express from 'express';
import { body, validationResult } from 'express-validator';
import axios from 'axios';
import Ticket from '../models/Ticket.js';

const router = express.Router();

// AI Service URL from environment
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

/**
 * POST /api/tickets
 * Create a new ticket and process it through AI pipeline
 */
router.post(
  '/tickets',
  [
    body('ticket_id').notEmpty().withMessage('Ticket ID is required'),
    body('customer_name').notEmpty().withMessage('Customer name is required'),
    body('customer_email').isEmail().withMessage('Valid email is required'),
    body('customer_tier').isIn(['bronze', 'silver', 'gold', 'platinum']).optional(),
    body('ticket_text').notEmpty().withMessage('Ticket description is required')
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const ticketData = req.body;

      // Create ticket in database with pending status
      const ticket = new Ticket({
        ...ticketData,
        status: 'pending'
      });
      await ticket.save();

      // Update status to processing
      ticket.status = 'processing';
      await ticket.save();

      // Call FastAPI AI service
      try {
        const aiResponse = await axios.post(
          `${AI_SERVICE_URL}/api/resolve-ticket`,
          ticketData,
          {
            timeout: 60000, // 60 second timeout
            headers: { 'Content-Type': 'application/json' }
          }
        );

        // Update ticket with AI resolution
        ticket.issue_type = aiResponse.data.issue_type;
        ticket.priority = aiResponse.data.priority;
        ticket.customer_response = aiResponse.data.customer_response;
        ticket.internal_notes = aiResponse.data.internal_notes;
        ticket.actions_to_take = aiResponse.data.actions_to_take;
        ticket.citations = aiResponse.data.citations;
        ticket.compliance_status = aiResponse.data.compliance_status;
        ticket.requires_escalation = aiResponse.data.requires_escalation;
        ticket.escalation_reason = aiResponse.data.escalation_reason;
        ticket.rewrite_count = aiResponse.data.rewrite_count;
        ticket.processing_time_ms = aiResponse.data.processing_time_ms;

        await ticket.markResolved();

        res.status(201).json({
          success: true,
          ticket: ticket.toObject()
        });

      } catch (aiError) {
        // AI service failed
        console.error('AI service error:', aiError.message);
        
        await ticket.markFailed(
          aiError.response?.data?.detail || aiError.message || 'AI service unavailable'
        );

        res.status(500).json({
          success: false,
          message: 'Failed to process ticket through AI service',
          error: aiError.message,
          ticket: ticket.toObject()
        });
      }

    } catch (error) {
      console.error('Ticket creation error:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to create ticket',
        error: error.message
      });
    }
  }
);

/**
 * GET /api/tickets
 * Get all tickets with optional filtering
 */
router.get('/tickets', async (req, res) => {
  try {
    const { status, customer_email, escalated, limit = 50, skip = 0 } = req.query;

    const query = {};
    if (status) query.status = status;
    if (customer_email) query.customer_email = customer_email.toLowerCase();
    if (escalated === 'true') query.requires_escalation = true;

    const tickets = await Ticket.find(query)
      .sort({ created_at: -1 })
      .limit(parseInt(limit))
      .skip(parseInt(skip));

    const total = await Ticket.countDocuments(query);

    res.json({
      success: true,
      tickets,
      total,
      limit: parseInt(limit),
      skip: parseInt(skip)
    });

  } catch (error) {
    console.error('Error fetching tickets:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch tickets',
      error: error.message
    });
  }
});

/**
 * GET /api/tickets/:ticketId
 * Get a specific ticket by ID
 */
router.get('/tickets/:ticketId', async (req, res) => {
  try {
    const ticket = await Ticket.findOne({ ticket_id: req.params.ticketId });

    if (!ticket) {
      return res.status(404).json({
        success: false,
        message: 'Ticket not found'
      });
    }

    res.json({
      success: true,
      ticket: ticket.toObject()
    });

  } catch (error) {
    console.error('Error fetching ticket:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch ticket',
      error: error.message
    });
  }
});

/**
 * GET /api/tickets/stats/summary
 * Get ticket statistics
 */
router.get('/stats/summary', async (req, res) => {
  try {
    const stats = await Ticket.getStats();

    res.json({
      success: true,
      stats
    });

  } catch (error) {
    console.error('Error fetching stats:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch statistics',
      error: error.message
    });
  }
});

/**
 * GET /api/tickets/escalated
 * Get all escalated tickets (for support dashboard)
 */
router.get('/escalated', async (req, res) => {
  try {
    const tickets = await Ticket.findEscalated();

    res.json({
      success: true,
      tickets,
      count: tickets.length
    });

  } catch (error) {
    console.error('Error fetching escalated tickets:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch escalated tickets',
      error: error.message
    });
  }
});

/**
 * PATCH /api/tickets/:ticketId/status
 * Update ticket status (for manual intervention)
 */
router.patch('/tickets/:ticketId/status', async (req, res) => {
  try {
    const { status, notes } = req.body;

    const ticket = await Ticket.findOne({ ticket_id: req.params.ticketId });

    if (!ticket) {
      return res.status(404).json({
        success: false,
        message: 'Ticket not found'
      });
    }

    ticket.status = status;
    if (notes) {
      ticket.internal_notes += `\n\n[Manual Update] ${notes}`;
    }

    await ticket.save();

    res.json({
      success: true,
      ticket: ticket.toObject()
    });

  } catch (error) {
    console.error('Error updating ticket:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update ticket',
      error: error.message
    });
  }
});

/**
 * DELETE /api/tickets/:ticketId
 * Delete a ticket (admin only, typically not used in production)
 */
router.delete('/tickets/:ticketId', async (req, res) => {
  try {
    const result = await Ticket.deleteOne({ ticket_id: req.params.ticketId });

    if (result.deletedCount === 0) {
      return res.status(404).json({
        success: false,
        message: 'Ticket not found'
      });
    }

    res.json({
      success: true,
      message: 'Ticket deleted successfully'
    });

  } catch (error) {
    console.error('Error deleting ticket:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete ticket',
      error: error.message
    });
  }
});

export default router;
