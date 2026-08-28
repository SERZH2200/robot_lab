from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.game import router as game_router
from backend.api.interpreter import router as interpreter_router
from backend.api.websocket import router as websocket_router
from backend.config import load_config
from backend.services.broadcaster import StateBroadcaster
from backend.services.game_service import GameService
from backend.services.interpreter_service import InterpreterService

#точка сбора всего back'а
#создаёт и настраивает FastAPI-приложение, связывая конфигурацию, игровые сервисы, API и frontend.
def create_app() -> FastAPI:
    config = load_config()

    app = FastAPI(
        title="Cell Robot Backend",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    game_service = GameService(#Создание единого GameService
        config.maze_dir,
        config.default_maze,
    )
    broadcaster = StateBroadcaster()#Создание бродкастера
    interpreter_service = InterpreterService(
        game_service,
        broadcaster,
    )
#app.state - место для объектов, которые должны жить столько же сколько всё приложение
    app.state.config = config
    app.state.game_service = game_service
    app.state.broadcaster = broadcaster
    app.state.interpreter_service = interpreter_service

    app.include_router(game_router)
    app.include_router(interpreter_router)
    app.include_router(websocket_router)

    #простой endpoint проверки того что backend запущен
    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    # Frontend лежит рядом с backend в корне проекта.
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

    if frontend_dir.is_dir():
        app.mount(
            "/frontend",
            StaticFiles(directory=frontend_dir),
            name="frontend",
        )

        @app.get("/", include_in_schema=False)
        async def frontend_index():
            return FileResponse(frontend_dir / "index.html")

    return app

#создание объекта приложения который запускает Uvicorn.
app = create_app()