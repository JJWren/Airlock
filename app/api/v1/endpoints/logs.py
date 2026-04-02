import asyncio
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from loguru import logger

router = APIRouter()

# A simple global queue to hold log messages
log_queue = asyncio.Queue()


# Add a sink to Loguru that puts messages into our queue
def log_sink(message):
    log_queue.put_nowait(message.record["message"])


logger.add(log_sink, level="DEBUG")


@router.get("/stream")
async def stream_logs():
    """Streams live application logs to the frontend."""

    async def log_generator():
        while True:
            message = await log_queue.get()
            yield {"data": message}

    return EventSourceResponse(log_generator())
