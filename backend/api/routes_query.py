from fastapi import APIRouter, HTTPException
from backend.models.schemas import QueryRequest, QueryResponse
from agents.orchestrator import orchestrator

router = APIRouter(prefix="/api", tags=["Agent Query"])

@router.post("/query", response_model=QueryResponse)
async def query_orca(request: QueryRequest):
    """Execute conversational agentic query pipeline."""
    try:
        response = await orchestrator.process_query(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ORCA Query Processing Error: {str(e)}")
