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
        source_url="https://nvd.nist.gov/vuln/detail/CVE-2021-28363",
        severity="HIGH",
        description="The urllib3 library 1.26.x before 1.26.4 for Python omits SSL certificate validation in some cases involving HTTPS to HTTPS proxies..."
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


@pytest.mark.asyncio
async def test_run_full_scan_fallback_to_keyword():
    """
    Ensures that if all CPEs return zero results, the service
    successfully falls back to a Keyword Search.
    """
    # 1. Arrange: Create a mock artifact and a 'Keyword' vulnerability
    mock_sbom = {
        "artifacts": [
            {
                "name": "flask",
                "version": "0.12.2",
                "cpes": [{"cpe": "cpe:2.3:a:wrong-vendor:flask:0.12.2:*:*:*:*:*:*:*"}]
            }
        ]
    }

    keyword_cve = CVEData(
        id="CVE-2018-1000656",  # Real Flask CVE
        source_url="https://nvd.nist.gov/vuln/detail/CVE-2018-1000656",
        severity="HIGH",
        base_score=7.5,
        description="The Flask Jinja2 environment config... could lead to remote code execution."
    )

    # 2. Act: Patch Syft and NVD services
    with patch("app.services.syft_service.SyftService.generate_sbom") as mock_syft:
        # We need to mock BOTH the CPE search and the Keyword search
        with patch("app.services.nvd_service.NVDService.get_cves_by_cpe", new_callable=AsyncMock) as mock_cpe:
            with patch("app.services.nvd_service.NVDService.get_cves_by_keyword",
                       new_callable=AsyncMock) as mock_keyword:
                # Setup: CPE returns nothing, Keyword returns the hit
                mock_syft.return_value = mock_sbom
                mock_cpe.return_value = []
                mock_keyword.return_value = [keyword_cve]

                service = CorrelationService()
                results = await service.run_full_scan("C:/fake/path")

    # 3. Assert: Verify the fallback happened
    assert len(results) == 1
    report = results[0]

    # The 'cpe' field should indicate a keyword match was used
    assert report.package_name == "flask"
    assert report.cpe == "NVD-KEYWORD-MATCH"
    assert report.vulnerabilities[0].id == "CVE-2018-1000656"

    # Ensure BOTH NVD methods were attempted
    mock_cpe.assert_called()
    mock_keyword.assert_called_once_with("flask", "0.12.2")
