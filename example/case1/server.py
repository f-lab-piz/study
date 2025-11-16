import random
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Adaptive TPS Test Server")

# True로 바꾸면 서버가 1% 확률로 503 에러를 리턴함.
ERROR_MODE = False


class WorkItem(BaseModel):
    item_id: int
    payload: str


class ServerState:
    """서버가 처리한 요청/실패 수를 단순 추적."""

    def __init__(self) -> None:
        self.inflight = 0
        self.completed = 0
        self.failed = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "inflight": self.inflight,
            "completed": self.completed,
            "failed": self.failed,
        }


state = ServerState()


@app.post("/work")
async def process_work(item: WorkItem):
    """즉시 응답하며 오류 플래그에 따라 1% 확률로 실패."""
    state.inflight += 1

    try:
        if ERROR_MODE and random.random() < 0.01:
            state.failed += 1
            raise HTTPException(status_code=503, detail="Injected error mode")

        state.completed += 1
        return {
            "item_id": item.item_id,
            "payload": item.payload,
            "error_mode": ERROR_MODE,
            "server_state": state.to_dict(),
        }
    finally:
        state.inflight -= 1
