import subprocess
import json
import os
from app.core.logger import log
from app.core import state


class SyftService:
    def __init__(self):
        self.bin_path = os.getenv("SYFT_BINARY_PATH", "/usr/local/bin/syft")

    def generate_sbom(self, target_path: str) -> dict:
        """Executes Syft and registers the PID for the kill-switch."""
        cmd = [self.bin_path, target_path, "-o", "json", "-q"]
        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Register PID globally
            state.active_scan_pid = process.pid
            log.debug(f"📑 Registered Syft PID: {process.pid}")

            stdout, stderr = process.communicate()
            state.active_scan_pid = None  # Clear on success

            if process.returncode != 0:
                log.error(f"❌ Syft failed: {stderr}")
                return {"artifacts": []}

            return json.loads(stdout)
        except Exception as e:
            state.active_scan_pid = None
            log.error(f"⚠️ Syft failure: {str(e)}")
            return {"artifacts": []}