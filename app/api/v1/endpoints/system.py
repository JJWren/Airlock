from fastapi import APIRouter, HTTPException
import os, signal
from app.core import state
from app.core.logger import log
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    """System heartbeat for the ConnectionStatus component."""
    return {"status": "ONLINE", "version": settings.app_version}


@router.post("/stop")
async def emergency_stop():
    """
    Tactical Kill-Switch: Terminates the entire process group immediately.

    """
    if state.active_scan_pid is not None:
        pid_to_kill = state.active_scan_pid
        try:
            log.warning(f"🛑 EMERGENCY STOP: Terminating process group for PID {pid_to_kill}")

            # Identify the process group and send SIGKILL to everything within it
            # This prevents orphaned 'syft' binaries from continuing to run and generate logs.
            os.killpg(os.getpgid(pid_to_kill), signal.SIGKILL)

            state.active_scan_pid = None
            log.error(f"🚨 CRITICAL: Sequence aborted. System resources released.")

            return {"status": "TERMINATED", "message": "Vetting group destroyed."}

        except Exception as e:
            state.active_scan_pid = None
            log.error(f"❌ Termination failure: {str(e)}")
            raise HTTPException(status_code=500, detail="System termination failure")

    return {"status": "IDLE", "message": "No active vetting sequence detected."}