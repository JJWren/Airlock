from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import List, Optional
from app.services.correlation_service import CorrelationService
from app.services.report_service import ReportService
from app.core.logger import log

router = APIRouter()
correlation_service = CorrelationService()
report_service = ReportService()


@router.post("/")
async def execute_scan(
        target_path: str = Form(...),
        files: Optional[List[UploadFile]] = File(None)
):
    """
    Tactical Vetting Engine with robust error handling.

    """
    try:
        findings = []
        total_pkgs = 0

        log.info(f"🚀 Initializing vetting sequence for: {target_path}")

        # 1. Input Processing Mode
        if files and len(files) > 0:
            log.info(f"📥 Processing {len(files)} manual manifest(s)")
            for file in files:
                content = await file.read()
                f, count = await correlation_service.analyze_manifest_content(
                    file.filename,
                    content.decode('utf-8')
                )
                findings.extend(f)
                total_pkgs += count
        else:
            # Fallback to local directory scan
            findings, total_pkgs = await correlation_service.scan_directory(target_path)

        # 2. Report Generation
        # Uses the refactored service to calculate CVSS and format metrics
        return report_service.generate_scan_result(findings, total_pkgs)

    except UnicodeDecodeError:
        log.error("❌ Encoding Error: Uploaded manifest is not a valid text file.")
        raise HTTPException(
            status_code=400,
            detail="Invalid file encoding. Use UTF-8 .txt or .json")

    except FileNotFoundError:
        log.error(f"❌ Path Error: Target directory '{target_path}' not found.")
        raise HTTPException(
            status_code=404,
            detail="Target directory does not exist on host.")

    except Exception as e:
        # Catch-all for vetting engine failures
        log.error(f"⚠️ Vetting Sequence Aborted: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal Engine Error: {type(e).__name__}"
        )
