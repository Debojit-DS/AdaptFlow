from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from api.models.api_schemas import DecisionRequest, DecisionResponse, SessionCreateRequest, SessionResponse
from api.session_store import session_store

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
def create_session(request: SessionCreateRequest) -> SessionResponse:
    return session_store.create(request)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str) -> SessionResponse:
    response = session_store.get(session_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return response


@router.post("/{session_id}/decision", response_model=DecisionResponse)
def apply_decision(session_id: str, request: DecisionRequest) -> DecisionResponse:
    response = session_store.apply_decision(session_id, request)
    if response is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return response


@router.websocket("/{session_id}/stream")
async def stream_session(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        record = session_store.get(session_id)
        if record is None:
            await websocket.send_json({"type": "error", "payload": {"stage": "unknown", "message": "Session not found"}})
            await websocket.close()
            return

        stages = [
            {"type": "stage_started", "payload": {"stage": "parse"}},
            {"type": "stage_progress", "payload": {"stage": "parse", "message": "Extracting actors and steps...", "percent": 30}},
            {"type": "stage_progress", "payload": {"stage": "parse", "message": "Identifying dependencies...", "percent": 70}},
            {"type": "stage_completed", "payload": {"stage": "parse", "data": {"parsed": record.parsed.model_dump()}}},
            {"type": "stage_started", "payload": {"stage": "diagnose"}},
            {"type": "stage_progress", "payload": {"stage": "diagnose", "message": "Analyzing workflow...", "percent": 50}},
            {"type": "stage_completed", "payload": {"stage": "diagnose", "data": {"before": record.graphs["before"].model_dump()}}},
            {"type": "stage_started", "payload": {"stage": "migrate"}},
            {"type": "stage_progress", "payload": {"stage": "migrate", "message": "Designing agent workflow...", "percent": 50}},
            {"type": "stage_completed", "payload": {"stage": "migrate", "data": {"after": record.graphs["after"].model_dump()}}},
            {"type": "stage_started", "payload": {"stage": "visualize"}},
            {"type": "stage_completed", "payload": {"stage": "visualize", "data": {}}},
        ]

        for event in stages:
            try:
                await websocket.send_json(event)
            except Exception:
                break
            import asyncio
            await asyncio.sleep(0.6)
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()
