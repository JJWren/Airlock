from fastapi import APIRouter, Response
from app.models.vulnerability import ScanResult
from app.services.report_service import ReportService

router = APIRouter()


@router.post("/pdf")
async def export_pdf_report(data: ScanResult):
    """Generates a PDF on the fly and returns it as a download."""
    # This calls the service your partner is working on
    report_gen = ReportService(data.findings)

    # We use an in-memory buffer so we don't have to manage temp files on disk
    pdf_content = report_gen.generate_pdf_buffer()

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Airlock_Audit_Report.pdf"}
    )
