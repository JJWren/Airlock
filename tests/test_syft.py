import pytest
import os
from app.services.syft_service import SyftService


def test_syft_can_scan_local_directory():
    """
    Verify that Syft can scan the current app directory and return a valid SBOM.
    Note: Requires Syft to be installed on your local machine to pass.
    """
    scanner = SyftService()

    # We use the 'app' directory as a test target
    target = os.path.abspath("app")

    # Act
    sbom = scanner.generate_sbom(target)

    # Assert
    assert isinstance(sbom, dict)
    assert "artifacts" in sbom  # Syft JSON always has an artifacts list
    assert len(sbom["artifacts"]) > 0

    # Check for a specific known package (like 'pydantic')
    package_names = [a["name"] for a in sbom["artifacts"]]
    assert any("pydantic" in name.lower() for name in package_names)