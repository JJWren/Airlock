import os
from unittest.mock import patch
from app.services.syft_service import SyftService
from app.core.config import get_settings


@patch.dict(os.environ, {"SYFT_BINARY_PATH": "syft"})
def test_syft_can_scan_local_directory():
    """
    Verify that Syft can scan the current app directory and return a valid SBOM.
    Note: Requires Syft to be installed on your local machine to pass.
    """
    # Arrange
    settings = get_settings()
    scanner = SyftService()

    # Target the project root where requirements.txt lives
    target = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Act
    sbom = scanner.generate_sbom(target)

    # Assert
    assert isinstance(sbom, dict), "The scanner must return a dictionary (SBOM)."
    assert "artifacts" in sbom, "Syft JSON output must contain an 'artifacts' list."
    assert len(sbom["artifacts"]) > 0, "The scan should have found at least one dependency"

    # Assert on structure rather than just one package name
    # Every artifact should have a name, version, and type
    for artifact in sbom["artifacts"][:10]: # Verify a sample of findings
        assert "name" in artifact, f"Artifact {artifact} is missing a name"
        assert "version" in artifact, f"Artifact {artifact.get('name')} is missing a version"
        assert "type" in artifact, f"Artifact {artifact.get('name')} is missing a type"