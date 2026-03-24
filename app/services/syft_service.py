import os, json, subprocess
from typing import Dict, Any, Optional
from app.core.config import get_settings, PROJECT_ROOT


class SyftService:
    """Internal service for interacting with the Syft CLI tool."""

    def __init__(self, binary_path: Optional[str] = None):
        """
        Initialize the service.
        If no path is provided, it pulls from the global settings.
        """
        settings = get_settings()
        raw_path = (binary_path or settings.syft_binary_path or "syft").strip('"')

        # Logic: If it looks like a relative path, anchor it to the Project Root
        if not os.path.isabs(raw_path) and raw_path != "syft":
            # This turns "bin/syft.exe" into "C:\...\Airlock\bin\syft.exe"
            self.binary_path = str((PROJECT_ROOT / raw_path).resolve())
        else:
            self.binary_path = raw_path

    def generate_sbom(self, target_path: str) -> Dict[str, Any]:
        """
        Executes Syft against a target directory and returns the JSON.
        """
        try:
            scan_target = f"dir:{target_path}"

            # -o JSON tells Syft to output the raw data structure
            # -q (quiet) suppresses the progress bars which would mess up stdout
            result = subprocess.run(
                [self.binary_path, scan_target, "-o", "json", "-q"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True
            )

            if not result.stdout:
                debug_info = f" | Stderr: {result.stderr}" if result.stderr else ""
                raise RuntimeError(f"Scanner Error: Syft produced no output.{debug_info}")

            # Parse the stdout string into a Python dictionary
            return json.loads(result.stdout)

        except subprocess.CalledProcessError as e:
            # If Syft fails, we capture the error and re-raise it for the API layer
            error_msg = e.stderr or "Syft execution failed with an unknown error."
            raise RuntimeError(f"Scanner Error: {error_msg}") from e
        except json.JSONDecodeError:
            raise RuntimeError("Scanner Error: Received invalid JSON from the Syft CLI.")
