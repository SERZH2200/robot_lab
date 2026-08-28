from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect


router = APIRouter()
#WebSocket - постоянное двустороннее соединение браузера и бэка
#WebSocket endpoint для отправки frontend обновлений состояния игры
@router.websocket("/ws/game")
async def game_websocket(websocket: WebSocket):
    app = websocket.app
    broadcaster = app.state.broadcaster

    await broadcaster.connect(websocket)#Handshake

    try:
        await websocket.send_json(#отправляется текущее состояние игры
            {
                "type": "state",
                "state": app.state.game_service.state(),
            }
        )

        while True:#удерживает WebSocket открытым и ждёт данные от клиента
            await websocket.receive_text()

    except WebSocketDisconnect:#закрытие вкладки/потеря соединения
        await broadcaster.disconnect(websocket)
