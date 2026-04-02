import subprocess
import json
import os
from app.core.logger import log
from app.core import state


class SyftService:
    def __init__(self):
        self.bin_path = os.getenv("SYFT_BINARY_PATH", "syft")

    def generate_sbom(self, target_path: str) -> dict:
        """Executes Syft and registers the PID for the kill-switch."""
        
        # Explicitly format target path for Syft (e.g. dir:/path/to/scan)
        formatted_target = f"dir:{target_path}" if os.path.isdir(target_path) else target_path

        cmd = [self.bin_path, formatted_target, "-o", "json", "-q"]
        try:
            # We explicitly enforce UTF-8 decoding to handle special characters smoothly.
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8"
            )

            # Register PID globally
            state.active_scan_pid = process.pid
            log.debug(f"📑 Registered Syft PID: {process.pid}")

            stdout, stderr = process.communicate()
            state.active_scan_pid = None  # Clear on success

            if process.returncode != 0:
                log.error(f"❌ Syft failed: {stderr}")
                return {"artifacts": []}
                
            if not stdout:
                log.error("❌ Syft failed: stdout is empty.")
                return {"artifacts": []}

            return json.loads(stdout)
        except Exception as e:
            state.active_scan_pid = None
            log.error(f"⚠️ Syft failure: {str(e)}")
            return {"artifacts": []}