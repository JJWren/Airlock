from app.services.nvd_service import NVDService
from app.models.vulnerability import CVEData


def test_get_cves_by_cpe_returns_list_of_cvedata():
    """
    Partner TDD TASK:
    1. Implement the NVDService.get_cves_by_cpe logic.
    2. Ensure it returns actual CVEData objects.
    3. Once passing, replace this multiline comment with a proper docstring.
    """
    service = NVDService()

    # Using a known legacy CPE that definitely has CVEs (Django 1.1)
    test_cpe = "cpe:2.3:a:djangoproject:django:1.1:*:*:*:*:*:*:*"

    # Act
    results = service.get_cves_by_cpe(test_cpe)

    # Assert
    assert isinstance(results, list), "Should return a list"
    if results:
        assert isinstance(results[0], CVEData), "Items in list must be CVEData objects"
        assert results[0].id.startswith("CVE-")