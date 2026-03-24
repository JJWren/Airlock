import os, json, subprocess
from typing import Dict, Any, Optional
from app.core.config import get_settings, PROJECT_ROOT
from app.core.logger import log


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

        log.info(f"🛠️ Syft Service loaded using binary: {self.binary_path}")

    def generate_sbom(self, target_path: str) -> Dict[str, Any]:
        """
        Executes Syft against a target directory and returns the JSON.
        """
        log.info(f"📁 Syft: Starting file analysis on {target_path}")

        result = None

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
                log.error("❌ Syft: CLI completed but produced an empty stdout.")
                raise RuntimeError("Scanner Error: Syft produced no output.")

            data = json.loads(result.stdout)
            package_count = len(data.get("artifacts", []))
            log.success(f"✅ Syft: Analysis complete. Found {package_count} artifacts.")
            return data


        except subprocess.CalledProcessError as e:
            log.error(f"❌ Syft CLI Error: {e.stderr}")
            raise RuntimeError(f"Scanner Error: {e.stderr}") from e

        except json.JSONDecodeError as e:
            # Provide debug context if the binary produces 'garbage' output
            stdout_len = len(result.stdout) if result and result.stdout else 0
            stderr_len = len(result.stderr) if result and result.stderr else 0
            log.error(
                f"❌ Syft: Failed to decode JSON output. "
                f"stdout_length={stdout_len}, stderr_length={stderr_len}"
            )
            raise RuntimeError("Scanner Error: Syft produced invalid JSON output.") from e
