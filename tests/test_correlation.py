import pytest
from unittest.mock import AsyncMock, patch
from app.services.correlation_service import CorrelationService
from app.models.vulnerability import CVEData


@pytest.mark.asyncio
async def test_run_full_scan_orchestration():
    """
    Verifies that CorrelationService correctly triggers the scanner,
    passes CPEs to the NVD service, and assembles the final report.
    """
    # 1. Arrange: Create dummy data to simulate Syft and NVD responses
    mock_sbom = {
        "artifacts": [
            {
                "name": "requests",
                "version": "2.25.1",
                "cpes": [
                    {"cpe": "cpe:2.3:a:python-requests:requests:2.25.1:*:*:*:*:*:*:*"}
                ]
            }
        ]
    }

    mock_cve = CVEData(
        id="CVE-2021-28363",
        source_url="https://nvd.nist.gov/vuln/detail/CVE-2026-28363",
        severity="HIGH",
        description="In OpenClaw before 2026.2.23, tools.exec.safeBins validation for sort could be bypassed..."
    )

    # 2. Act: Patch the internal services so we don't run real binaries or APIs
    with patch("app.services.syft_service.SyftService.generate_sbom") as mock_syft:
        with patch("app.services.nvd_service.NVDService.get_cves_by_cpe", new_callable=AsyncMock) as mock_nvd:
            # Set the "Fake" return values
            mock_syft.return_value = mock_sbom
            mock_nvd.return_value = [mock_cve]

            service = CorrelationService()
            results = await service.run_full_scan("C:/fake/path")

    # 3. Assert: Verify the "Airlock" Handshake
    assert len(results) == 1
    report = results[0]

    # Check that data was mapped correctly to your VulnerabilityReport model
    assert report.package_name == "requests"
    assert len(report.vulnerabilities) == 1
    assert report.vulnerabilities[0].id == "CVE-2021-28363"

    # Verify the services were actually called with the right data
    mock_syft.assert_called_once_with("C:/fake/path")
    mock_nvd.assert_called_once_with("cpe:2.3:a:python-requests:requests:2.25.1:*:*:*:*:*:*:*")