import subprocess
import json
from typing import Dict, Any, Optional


class SyftService:
    """Internal service for interacting with the Syft CLI tool."""

    def __init__(self, binary_path: str = "syft"):
        """
        Initialize the service.
        In Docker, 'syft' will be in the PATH. Locally, you may need a full path.
        """
        self.binary_path = binary_path

    def generate_sbom(self, target_path: str) -> Dict[str, Any]:
        """
        Executes Syft against a target directory and returns the CycloneDX JSON.
        """
        try:
            # -o JSON tells Syft to output the raw data structure
            # -q (quiet) suppresses the progress bars which would mess up stdout
            result = subprocess.run(
                [self.binary_path, target_path, "-o", "json", "-q"],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse the stdout string into a Python dictionary
            return json.loads(result.stdout)

        except subprocess.CalledProcessError as e:
            # If Syft fails, we capture the error and re-raise it for the API layer
            error_msg = e.stderr or "Syft execution failed with an unknown error."
            raise RuntimeError(f"Scanner Error: {error_msg}")
        except json.JSONDecodeError:
            raise RuntimeError("Scanner Error: Received invalid JSON from the Syft CLI.")
        