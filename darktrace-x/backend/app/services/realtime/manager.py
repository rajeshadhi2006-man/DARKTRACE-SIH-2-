import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import WebSocket

logger = logging.getLogger("darktrace.realtime")

class ConnectionManager:
    """
    Real-Time WebSocket Connection & Telemetry Manager.
    Broadcasts live dark web intercepts, crawler updates, and KPI changes
    to all active investigator consoles.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self._loop = asyncio.get_running_loop()
        logger.info(f"WebSocket client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcasts a JSON message payload to all connected WebSocket clients."""
        if not self.active_connections:
            return
        payload = json.dumps(message)
        dead_connections = []
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)

    def broadcast_sync(self, message: Dict[str, Any]):
        """Broadcasts synchronously from background worker threads into main asyncio loop."""
        try:
            if self._loop and self._loop.is_running():
                asyncio.run_coroutine_threadsafe(self.broadcast(message), self._loop)
            else:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.broadcast(message))
        except Exception as e:
            logger.warning(f"broadcast_sync error: {e}")

ws_manager = ConnectionManager()
