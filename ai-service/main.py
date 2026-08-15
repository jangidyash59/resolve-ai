"""
FastAPI AI Microservice for ResolveAI
Handles customer support ticket resolution using CrewAI agents and FAISS RAG
Powered by Grok API (xAI) - Free and Fast!
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import sys
from pathlib import Path
from typing import Optional, List
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.models import TicketInput, OrderContext, OrderItem, CustomerTier
from src.orchestrator_simple import SupportOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ResolveAI API",
    description="AI-powered customer support ticket resolution microservice",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - Allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev
        "http://localhost:5173",  # Vite dev
        "https://*.vercel.app",   # Vercel deployments
        os.getenv("FRONTEND_URL", "*")  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator: Optional[SupportOrchestrator] = None


# Request/Response Models for API
class OrderItemRequest(BaseModel):
    """Order item in API request"""
    name: str
    sku: Optional[str] = ""
    category: Optional[str] = ""
    price: float
    quantity: int = 1


class OrderContextRequest(BaseModel):
    """Order context in API request"""
    order_id: str
    order_date: str
    delivery_date: Optional[str] = None
    estimated_delivery: Optional[str] = None
    items: List[OrderItemRequest] = []
    total_amount: float
    payment_method: str = "credit_card"
    shipping_method: str = "standard"
    shipping_address_country: str = "US"
    shipping_address_state: Optional[str] = None
    seller_type: str = "direct"
    seller_name: Optional[str] = None


class TicketRequest(BaseModel):
    """API request model for ticket resolution"""
    ticket_id: str
    customer_name: str
    customer_email: str
    customer_tier: str = "bronze"
    ticket_text: str
    order_context: Optional[OrderContextRequest] = None


class TicketResponse(BaseModel):
    """API response model for resolved ticket"""
    ticket_id: str
    issue_type: str
    priority: str
    customer_response: str
    internal_notes: str
    actions_to_take: List[str]
    citations: List[str]
    compliance_status: str
    requires_escalation: bool
    escalation_reason: str
    rewrite_count: int
    processing_time_ms: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    faiss_initialized: bool


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the AI orchestrator on startup"""
    global orchestrator
    try:
        logger.info("Initializing ResolveAI orchestrator...")
        orchestrator = SupportOrchestrator()
        logger.info("✓ Orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {str(e)}")
        raise


# Health check endpoint
@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy" if orchestrator else "initializing",
        service="ResolveAI AI Service",
        version="1.0.0",
        faiss_initialized=orchestrator is not None
    )


# Main ticket resolution endpoint
@app.post("/api/resolve-ticket", response_model=TicketResponse)
async def resolve_ticket(ticket_request: TicketRequest):
    """
    Resolve a customer support ticket using AI agents
    
    Process:
    1. Triage: Classify issue and check escalation
    2. Retrieval: Query FAISS vector database for relevant policies
    3. Resolution: Draft response with citations
    4. Compliance: Audit response for accuracy and safety
    """
    if not orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is still initializing. Please try again in a moment."
        )
    
    try:
        import time
        start_time = time.time()
        
        # Convert API request to internal model
        order_ctx = None
        if ticket_request.order_context:
            order_ctx = OrderContext(
                order_id=ticket_request.order_context.order_id,
                order_date=ticket_request.order_context.order_date,
                delivery_date=ticket_request.order_context.delivery_date,
                estimated_delivery=ticket_request.order_context.estimated_delivery,
                items=[
                    OrderItem(
                        name=item.name,
                        sku=item.sku,
                        category=item.category,
                        price=item.price,
                        quantity=item.quantity
                    )
                    for item in ticket_request.order_context.items
                ],
                total_amount=ticket_request.order_context.total_amount,
                payment_method=ticket_request.order_context.payment_method,
                shipping_method=ticket_request.order_context.shipping_method,
                shipping_address_country=ticket_request.order_context.shipping_address_country,
                shipping_address_state=ticket_request.order_context.shipping_address_state,
                seller_type=ticket_request.order_context.seller_type,
                seller_name=ticket_request.order_context.seller_name
            )
        
        # Map customer tier string to enum
        tier_map = {
            "bronze": CustomerTier.BRONZE,
            "silver": CustomerTier.SILVER,
            "gold": CustomerTier.GOLD,
            "platinum": CustomerTier.PLATINUM
        }
        customer_tier = tier_map.get(ticket_request.customer_tier.lower(), CustomerTier.BRONZE)
        
        ticket_input = TicketInput(
            ticket_id=ticket_request.ticket_id,
            customer_name=ticket_request.customer_name,
            customer_email=ticket_request.customer_email,
            customer_tier=customer_tier,
            ticket_text=ticket_request.ticket_text,
            order_context=order_ctx
        )
        
        # Process ticket through AI pipeline
        logger.info(f"Processing ticket {ticket_request.ticket_id}")
        result = orchestrator.resolve_ticket(ticket_input)
        
        processing_time_ms = (time.time() - start_time) * 1000
        logger.info(f"✓ Ticket {ticket_request.ticket_id} resolved in {processing_time_ms:.0f}ms")
        
        # Convert to API response
        return TicketResponse(
            ticket_id=result.ticket_id,
            issue_type=result.issue_type,
            priority=result.priority,
            customer_response=result.customer_response,
            internal_notes=result.internal_notes,
            actions_to_take=result.actions_to_take,
            citations=result.citations,
            compliance_status=result.compliance_status,
            requires_escalation=result.requires_escalation,
            escalation_reason=result.escalation_reason,
            rewrite_count=result.rewrite_count,
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        logger.error(f"Error processing ticket {ticket_request.ticket_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process ticket: {str(e)}"
        )


# Policy search endpoint (optional, for debugging/testing)
@app.post("/api/search-policies")
async def search_policies_endpoint(query: str, k: int = 3):
    """Search policy documents directly (for debugging)"""
    if not orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is still initializing"
        )
    
    try:
        from src.orchestrator_simple import search_policies
        results = search_policies(query, k)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
