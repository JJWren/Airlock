import pytest
from unittest.mock import MagicMock, patch
from app.services.nvd_service import NVDService
from app.models.vulnerability import CVEData


@patch("app.services.nvd_service.nvdlib.searchCVE")
def test_get_cves_by_cpe_with_mock(mock_search):
    """
    Verified Lead Test: Ensures NVDService maps raw NIST objects to CVEData
    without making actual network calls.
    """
    # 1. Create a mock CVE object resembling an NVDLib response
    mock_cve = MagicMock()
    mock_cve.id = "CVE-2026-12345"
    mock_cve.descriptions = [MagicMock(value="Test vulnerability description")]
    mock_cve.v31score = 7.5
    mock_cve.v31severity = "HIGH"

    # Configure the mock to return our fake CVE in a list
    mock_search.return_value = [mock_cve]

    service = NVDService()
    test_cpe = "cpe:2.3:a:test:product:1.0:*:*:*:*:*:*:*"

    # 2. Act
    results = service.get_cves_by_cpe(test_cpe)

    # 3. Assert
    assert len(results) == 1
    assert isinstance(results[0], CVEData)
    assert results[0].id == "CVE-2026-12345"
    assert results[0].base_score == 7.5
    assert results[0].severity == "HIGH"

    # Verify the API was called with the correct parameters
    mock_search.assert_called_once()