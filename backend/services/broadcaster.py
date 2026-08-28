from __future__ import annotations

import asyncio

from fastapi import WebSocket


class StateBroadcaster:#хранит активные WebSocket-соединения и отправляет им JSON
    def __init__(self):
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        async with self._lock:
            connections = list(self._connections)

        dead: list[WebSocket] = []
        for connection in connections:
            try:
                await connection.send_json(payload)
            except Exception:
                dead.append(connection)

        if dead:#Удаление неисправных соединений
            async with self._lock:
                for connection in dead:
                    self._connections.discard(connection)
