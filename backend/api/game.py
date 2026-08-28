from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from backend.api.schemas import MazeLoadRequest


router = APIRouter(prefix="/api/game", tags=["game"])

#HTTP API игрового сервера. Принимаются запросы с front, вызывается GameService, рассылаются
@router.get("/state")
async def get_state(request: Request):
    return request.app.state.game_service.state()#возвращает состояния


@router.get("/mazes")
async def get_mazes(request: Request):
    return {
        "mazes": request.app.state.game_service.list_mazes(),#возвращает файлы из mazes
    }


@router.post("/load")
async def load_maze_endpoint(payload: MazeLoadRequest, request: Request):#Загрузка лабиринта
    try:
        state = request.app.state.game_service.load(payload.name)
    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    await request.app.state.broadcaster.broadcast(
        {
            "type": "state",
            "state": state,
        }
    )
    return state


@router.post("/reset")#сброс игры
async def reset_game(request: Request):
    state = request.app.state.game_service.reset()
    await request.app.state.broadcaster.broadcast(
        {
            "type": "state",
            "state": state,
        }
    )
    return state


@router.post("/move/{direction}")#перемещение робота
async def move_robot(direction: str, request: Request):
    try:
        result, state = request.app.state.game_service.move(direction)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    await request.app.state.broadcaster.broadcast(
        {
            "type": "state",
            "state": state,
        }
    )

    return {
        "result": result,
        "state": state,
    }


@router.post("/lms")#сканер
async def run_lms(request: Request):
    result, state = request.app.state.game_service.lms()

    await request.app.state.broadcaster.broadcast(
        {
            "type": "state",
            "state": state,
        }
    )

    return {
        "result": result,
        "state": state,
    }
