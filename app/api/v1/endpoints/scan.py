from fastapi import APIRouter, HTTPException
from typing import List
from app.models.scan import ScanRequest
from app.models.vulnerability import VulnerabilityReport
from app.services.correlation_service import CorrelationService

router = APIRouter()


@router.post("/scan", response_model=List[VulnerabilityReport])
async def trigger_scan(request: ScanRequest):
    """
    Triggers a full 'Airlock' scan:
    1. Generates SBOM via Syft.
    2. Enriches findings via NIST NVD.
    3. Returns a correlated security report.
    """
    service = CorrelationService()

    try:
        # The 'brain' of the app handles the orchestration
        results = await service.run_full_scan(request.target_path)
        return results

    except RuntimeError as e:
        # Catch scanner/binary errors and return a 400
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch unexpected crashes and return a 500
        raise HTTPException(status_code=500, detail="An internal error occurred during enrichment.")