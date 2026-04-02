from io import BytesIO
from fpdf import FPDF
from app.models.vulnerability import ScanResult, VulnerabilityReport
from app.core.logger import log


class ReportService:
    """Handles the transformation of raw vetting findings into structured reports."""

    def __init__(self, findings: list[VulnerabilityReport] = None):
        """Initialize with findings for instance-based reporting."""
        self.findings = findings or []

    @staticmethod
    def generate_scan_result(findings: list[VulnerabilityReport], total_packages: int) -> ScanResult:
        """Calculates summary metrics for the frontend."""
        summary = {
            "total_packages": total_packages,
            "vulnerable_packages": len(findings),
            "critical_count": 0,
            "high_count": 0
        }

        for report in findings:
            for vuln in report.vulnerabilities:
                if vuln.severity == "CRITICAL":
                    summary["critical_count"] += 1
                elif vuln.severity == "HIGH":
                    summary["high_count"] += 1

        return ScanResult(summary=summary, findings=findings)

    def generate_pdf_buffer(self) -> bytes:
        """
        Generates a tactical PDF report in-memory without disk I/O.
        """
        pdf = FPDF()
        pdf.add_page()

        # Tactical Header
        pdf.set_font("Courier", "B", 16)
        pdf.cell(0, 10, "AIRLOCK: SECURITY AUDIT REPORT", ln=True, align="C")
        pdf.ln(10)

        # Inventory Summary
        pdf.set_font("Courier", "B", 12)
        pdf.cell(0, 10, f"VULNERABLE PACKAGES IDENTIFIED: {len(self.findings)}", ln=True)
        pdf.ln(5)

        # Detailed Findings
        pdf.set_font("Courier", "", 10)
        for report in self.findings:
            pdf.set_text_color(239, 68, 68)  # Tertiary Red for visibility
            pdf.cell(0, 10, f">> PACKAGE: {report.package_name} v{report.installed_version}", ln=True)
            pdf.set_text_color(0, 0, 0)

            for vuln in report.vulnerabilities:
                pdf.multi_cell(0, 5, f"   [{vuln.id}] SEVERITY: {vuln.severity} (Score: {vuln.base_score})")
                pdf.multi_cell(0, 5, f"   DESC: {vuln.description[:150]}...")
                pdf.ln(2)

        # Return the buffer content
        return pdf.output()

    @staticmethod
    def export_to_json(result: ScanResult) -> str:
        """Helper for log exporting."""
        return result.model_dump_json()