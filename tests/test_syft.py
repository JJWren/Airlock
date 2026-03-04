import os
from app.services.syft_service import SyftService


def test_syft_can_scan_local_directory():
    """
    Verify that Syft can scan the current app directory and return a valid SBOM.
    Note: Requires Syft to be installed on your local machine to pass.
    """
    scanner = SyftService()

    # Target the project root where requirements.txt lives
    target = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Act
    sbom = scanner.generate_sbom(target)

    # Assert
    assert isinstance(sbom, dict)
    assert "artifacts" in sbom  # Syft JSON always has an artifacts list
    assert len(sbom["artifacts"]) > 0

    # Assert on structure rather than just one package name
    # Every artifact should have a name, version, and type
    for artifact in sbom["artifacts"][:5]:  # Check first few for speed
        assert "name" in artifact
        assert "version" in artifact
        assert "type" in artifact
