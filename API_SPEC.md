# ResolveAI API Specification

Complete API documentation for the ResolveAI microservices architecture.

---

## Table of Contents

1. [Overview](#overview)
2. [Base URLs](#base-urls)
3. [Authentication](#authentication)
4. [Express API Gateway](#express-api-gateway)
5. [FastAPI AI Service](#fastapi-ai-service)
6. [Data Models](#data-models)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## Overview

ResolveAI exposes two primary API services:

1. **Express API Gateway** - Main entry point for client applications
2. **FastAPI AI Service** - Internal AI processing engine (can be called directly for testing)

### Architecture Flow

```
Client → Express Gateway → FastAPI AI Service
                ↓
          MongoDB Database
```

---

## Base URLs

### Development
- **Express Gateway:** `http://localhost:5000`
- **FastAPI Service:** `http://localhost:8000`
- **Frontend:** `http://localhost:3000`

### Production
- **Express Gateway:** `https://resolveai-api-gateway.onrender.com`
- **FastAPI Service:** `https://resolveai-ai-service.onrender.com`
- **Frontend:** `https://resolveai.vercel.app`

---

## Authentication

Currently, the API does not require authentication. **This is suitable for demos and portfolios.**

### Future Enhancement (Optional)

For production systems, consider adding:
- JWT (JSON Web Tokens) for session management
- API Keys for service-to-service communication
- OAuth 2.0 for third-party integrations

Example protected endpoint:
```http
GET /api/tickets
Authorization: Bearer <JWT_TOKEN>
```

---

## Express API Gateway

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check API gateway status and dependencies

**Response:**
```json
{
  "uptime": 12345.67,
  "status": "OK",
  "timestamp": 1709587200000,
  "mongodb": "connected"
}
```

**Status Codes:**
- `200` - Service healthy
- `503` - Service unavailable

---

### 2. Root Endpoint

**Endpoint:** `GET /`

**Description:** Get service information

**Response:**
```json
{
  "service": "ResolveAI API Gateway",
  "version": "2.0.0",
  "status": "healthy",
  "timestamp": "2026-03-28T10:30:00.000Z",
  "connections": {
    "mongodb": "connected",
    "ai_service": "http://localhost:8000"
  }
}
```

---

### 3. Create Ticket

**Endpoint:** `POST /api/tickets`

**Description:** Submit a new support ticket and process it through AI pipeline

**Request Body:**
```json
{
  "ticket_id": "TKT-001",
  "customer_name": "Arjun Sharma",
  "customer_email": "arjun@example.com",
  "customer_tier": "silver",
  "ticket_text": "My order was damaged during shipping. Need full refund.",
  "order_context": {
    "order_id": "ORD-2026-99001",
    "order_date": "2026-03-25",
    "delivery_date": "2026-03-27",
    "items": [
      {
        "name": "Wireless Bluetooth Speaker",
        "sku": "WBS-001",
        "category": "electronics",
        "price": 149.99,
        "quantity": 1
      }
    ],
    "total_amount": 149.99,
    "payment_method": "credit_card",
    "shipping_method": "standard",
    "shipping_address_country": "IN",
    "shipping_address_state": "Maharashtra",
    "seller_type": "direct",
    "seller_name": null
  }
}
```

**Required Fields:**
- `ticket_id` (string)
- `customer_name` (string)
- `customer_email` (valid email)
- `ticket_text` (string, min 10 characters)

**Optional Fields:**
- `customer_tier` (enum: bronze, silver, gold, platinum)
- `order_context` (object, see schema below)

**Response (Success):**
```json
{
  "success": true,
  "ticket": {
    "_id": "65f8a1b2c3d4e5f6g7h8i9j0",
    "ticket_id": "TKT-001",
    "customer_name": "Arjun Sharma",
    "customer_email": "arjun@example.com",
    "customer_tier": "silver",
    "ticket_text": "My order was damaged during shipping...",
    "order_context": { ... },
    "status": "resolved",
    "issue_type": "refund",
    "priority": "high",
    "customer_response": "I understand your package arrived damaged. Based on our Damaged Items policy, you are eligible for a full refund...",
    "internal_notes": "Customer reported damaged item upon delivery. Package shows visible damage...",
    "actions_to_take": [
      "Process full refund of $149.99",
      "Arrange return pickup",
      "Investigate shipping carrier"
    ],
    "citations": [
      "returns_refunds.md — Damaged Items",
      "shipping_domestic.md — Shipping Damage Claims"
    ],
    "compliance_status": "approved",
    "requires_escalation": false,
    "escalation_reason": "",
    "rewrite_count": 0,
    "processing_time_ms": 28450,
    "created_at": "2026-03-28T10:30:00.000Z",
    "updated_at": "2026-03-28T10:30:28.450Z",
    "resolved_at": "2026-03-28T10:30:28.450Z"
  }
}
```

**Response (Error - AI Service Failed):**
```json
{
  "success": false,
  "message": "Failed to process ticket through AI service",
  "error": "Connection timeout",
  "ticket": {
    "_id": "65f8a1b2c3d4e5f6g7h8i9j0",
    "ticket_id": "TKT-001",
    "status": "failed",
    "error_message": "AI service unavailable"
  }
}
```

**Status Codes:**
- `201` - Ticket created and resolved
- `400` - Validation error
- `500` - Server error or AI service unavailable

---

### 4. Get All Tickets

**Endpoint:** `GET /api/tickets`

**Description:** Retrieve tickets with optional filtering

**Query Parameters:**
- `status` (optional) - Filter by status: pending, processing, resolved, escalated, failed
- `customer_email` (optional) - Filter by customer email
- `escalated` (optional) - Filter escalated tickets: true/false
- `limit` (optional, default: 50) - Number of results
- `skip` (optional, default: 0) - Pagination offset

**Examples:**
```http
GET /api/tickets?status=resolved&limit=20
GET /api/tickets?customer_email=arjun@example.com
GET /api/tickets?escalated=true
```

**Response:**
```json
{
  "success": true,
  "tickets": [
    {
      "ticket_id": "TKT-001",
      "customer_name": "Arjun Sharma",
      "status": "resolved",
      "issue_type": "refund",
      "priority": "high",
      "created_at": "2026-03-28T10:30:00.000Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "skip": 0
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

---

### 5. Get Ticket by ID

**Endpoint:** `GET /api/tickets/:ticketId`

**Description:** Retrieve a specific ticket by ticket_id

**Example:**
```http
GET /api/tickets/TKT-001
```

**Response:**
```json
{
  "success": true,
  "ticket": {
    "ticket_id": "TKT-001",
    "customer_name": "Arjun Sharma",
    "customer_email": "arjun@example.com",
    "status": "resolved",
    "customer_response": "...",
    "citations": [...],
    "created_at": "2026-03-28T10:30:00.000Z"
  }
}
```

**Status Codes:**
- `200` - Ticket found
- `404` - Ticket not found
- `500` - Server error

---

### 6. Get Statistics

**Endpoint:** `GET /api/stats/summary`

**Description:** Get aggregate ticket statistics

**Response:**
```json
{
  "success": true,
  "stats": {
    "total": 250,
    "resolved": 200,
    "escalated": 25,
    "pending": 15,
    "resolution_rate": "80.00",
    "escalation_rate": "10.00",
    "avg_processing_time_ms": 26780
  }
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

---

### 7. Get Escalated Tickets

**Endpoint:** `GET /api/escalated`

**Description:** Get all tickets requiring human review

**Response:**
```json
{
  "success": true,
  "tickets": [
    {
      "ticket_id": "TKT-005",
      "customer_name": "John Doe",
      "requires_escalation": true,
      "escalation_reason": "Legal threat detected",
      "status": "escalated",
      "created_at": "2026-03-28T09:00:00.000Z"
    }
  ],
  "count": 25
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

---

### 8. Update Ticket Status

**Endpoint:** `PATCH /api/tickets/:ticketId/status`

**Description:** Manually update ticket status (for support agents)

**Request Body:**
```json
{
  "status": "resolved",
  "notes": "Manually resolved by support agent after verification"
}
```

**Response:**
```json
{
  "success": true,
  "ticket": {
    "ticket_id": "TKT-001",
    "status": "resolved",
    "internal_notes": "...\n\n[Manual Update] Manually resolved by support agent after verification"
  }
}
```

**Status Codes:**
- `200` - Updated successfully
- `404` - Ticket not found
- `500` - Server error

---

### 9. Delete Ticket

**Endpoint:** `DELETE /api/tickets/:ticketId`

**Description:** Delete a ticket (admin only, typically not used in production)

**Response:**
```json
{
  "success": true,
  "message": "Ticket deleted successfully"
}
```

**Status Codes:**
- `200` - Deleted successfully
- `404` - Ticket not found
- `500` - Server error

---

## FastAPI AI Service

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check AI service status

**Response:**
```json
{
  "status": "healthy",
  "service": "ResolveAI AI Service",
  "version": "2.0.0",
  "faiss_initialized": true
}
```

**Status Codes:**
- `200` - Service healthy
- `503` - Service initializing

---

### 2. Resolve Ticket

**Endpoint:** `POST /api/resolve-ticket`

**Description:** Process ticket through AI pipeline (4 agents)

**Request Body:** Same as Express `/api/tickets`

**Response:**
```json
{
  "ticket_id": "TKT-001",
  "issue_type": "refund",
  "priority": "high",
  "customer_response": "I understand your package arrived damaged...",
  "internal_notes": "Customer reported damaged item...",
  "actions_to_take": [
    "Process full refund of $149.99",
    "Arrange return pickup"
  ],
  "citations": [
    "returns_refunds.md — Damaged Items"
  ],
  "compliance_status": "approved",
  "requires_escalation": false,
  "escalation_reason": "",
  "rewrite_count": 0,
  "processing_time_ms": 28450
}
```

**Status Codes:**
- `200` - Success
- `503` - Service initializing
- `500` - Processing error

---

### 3. Search Policies

**Endpoint:** `POST /api/search-policies`

**Description:** Debug endpoint to search policy documents directly

**Query Parameters:**
- `query` (required) - Search query
- `k` (optional, default: 3) - Number of results

**Example:**
```http
POST /api/search-policies?query=refund damaged items&k=3
```

**Response:**
```json
{
  "query": "refund damaged items",
  "results": [
    {
      "id": "returns_refunds-section-2-chunk-0",
      "text": "Damaged Items: If you receive a damaged product...",
      "source": "returns_refunds.md",
      "section": "Damaged Items",
      "citation": "returns_refunds.md — Damaged Items",
      "similarity": 0.8765
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `503` - Service not ready
- `500` - Search error

---

## Data Models

### Ticket Schema

```typescript
interface Ticket {
  // Identification
  ticket_id: string;                    // Unique ticket identifier
  _id?: string;                         // MongoDB ObjectId
  
  // Customer Information
  customer_name: string;                // Customer's full name
  customer_email: string;               // Valid email address
  customer_tier: 'bronze' | 'silver' | 'gold' | 'platinum';
  
  // Ticket Content
  ticket_text: string;                  // Free-form issue description
  order_context?: OrderContext;         // Optional order details
  
  // AI Resolution
  issue_type?: string;                  // Classified issue type
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  customer_response?: string;           // AI-generated response
  internal_notes?: string;              // Agent-only notes
  actions_to_take?: string[];           // Required actions
  citations?: string[];                 // Policy citations
  
  // Status Tracking
  status: 'pending' | 'processing' | 'resolved' | 'escalated' | 'failed';
  compliance_status?: string;           // Compliance check result
  requires_escalation: boolean;         // Human review required
  escalation_reason?: string;           // Reason for escalation
  rewrite_count?: number;               // Compliance rewrites
  
  // Metadata
  processing_time_ms?: number;          // AI processing time
  error_message?: string;               // Error if failed
  created_at: Date;                     // Creation timestamp
  updated_at: Date;                     // Last update
  resolved_at?: Date;                   // Resolution timestamp
}
```

### OrderContext Schema

```typescript
interface OrderContext {
  order_id: string;
  order_date: string;                   // YYYY-MM-DD
  delivery_date?: string;               // YYYY-MM-DD
  estimated_delivery?: string;          // YYYY-MM-DD
  items: OrderItem[];
  total_amount: number;
  payment_method: 'credit_card' | 'upi' | 'cash_on_delivery';
  shipping_method: 'standard' | 'expedited' | 'overnight';
  shipping_address_country: string;     // ISO code
  shipping_address_state?: string;
  seller_type: 'direct' | 'marketplace';
  seller_name?: string;
}
```

### OrderItem Schema

```typescript
interface OrderItem {
  name: string;
  sku?: string;
  category?: string;
  price: number;
  quantity: number;
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error message",
  "errors": [
    {
      "field": "customer_email",
      "message": "Valid email is required"
    }
  ]
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PATCH, DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Validation error |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service initializing or down |

---

## Rate Limiting

### Express API Gateway

- **Limit:** 100 requests per 15 minutes per IP address
- **Headers:**
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time when limit resets

**Rate Limit Exceeded Response:**
```json
{
  "success": false,
  "message": "Too many requests from this IP, please try again later."
}
```
Status Code: `429 Too Many Requests`

---

## CORS Configuration

### Allowed Origins

**Development:**
- http://localhost:3000
- http://localhost:5173

**Production:**
- https://*.vercel.app (all Vercel deployments)
- Configured FRONTEND_URL environment variable

### Allowed Methods
- GET, POST, PATCH, DELETE, OPTIONS

### Allowed Headers
- Content-Type, Authorization

---

## Example cURL Commands

### Create Ticket
```bash
curl -X POST http://localhost:5000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-001",
    "customer_name": "Test User",
    "customer_email": "test@example.com",
    "customer_tier": "silver",
    "ticket_text": "My package was damaged during shipping"
  }'
```

### Get All Tickets
```bash
curl http://localhost:5000/api/tickets?limit=10
```

### Get Statistics
```bash
curl http://localhost:5000/api/stats/summary
```

### Health Check
```bash
curl http://localhost:5000/health
curl http://localhost:8000/health
```

---

## Webhooks (Future Enhancement)

For production systems, consider adding webhooks to notify external systems:

```http
POST https://your-app.com/webhooks/ticket-resolved
Content-Type: application/json

{
  "event": "ticket.resolved",
  "timestamp": "2026-03-28T10:30:00.000Z",
  "ticket_id": "TKT-001",
  "status": "resolved"
}
```

---

**Last Updated:** March 2026  
**API Version:** 2.0.0
