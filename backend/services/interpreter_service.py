from __future__ import annotations

import asyncio

from backend.robot_api.game_robot_adapter import GameRobotAdapter
from backend.services.broadcaster import StateBroadcaster
from backend.services.game_service import GameService


class InterpreterService:
    def __init__(
        self,
        game_service: GameService,
        broadcaster: StateBroadcaster,
    ):
        self.game_service = game_service
        self.broadcaster = broadcaster

    async def run(self, source: str) -> dict:
        from language.runner import format_value, run_source

        loop = asyncio.get_running_loop()#текущий цикл событий FastAPI

        def notify(state: dict) -> None:
#coroutine асинхронная функция, выполнение можно ставить на паузу и возобновлять позже
            asyncio.run_coroutine_threadsafe(
                self.broadcaster.broadcast(
                    {
                        "type": "state",
                        "state": state,
                    }
                ),
                loop,
            )

        robot = GameRobotAdapter(
            self.game_service.engine,
            on_state_change=notify,
        )

        result = await asyncio.to_thread(#чтобы не блокировать event_loop, программа в отдельном потоке
            run_source,
            source,
            robot,
        )

        state = self.game_service.state()
        await self.broadcaster.broadcast(
            {
                "type": "program_finished",
                "result": format_value(result),
                "state": state,
            }
        )

        return {
            "result": format_value(result),
            "state": state,
        }
