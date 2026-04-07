from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, Request
from env.models import ActionModel, ActionType, ObservationModel, FullStateModel
from server.schemas import ResetRequest, ResetResponse, StateResponse, StepRequest, StepResponse
from server.session import session_manager

router = APIRouter()
DEFAULT_SESSION = "default"


@router.get("/metadata")
async def metadata():
    return {
        "name": "customer-support-env",
        "description": "OpenEnv benchmark for customer support ticket workflows.",
    }


@router.get("/schema")
async def schema():
    return {
        "action": ActionModel.model_json_schema(),
        "observation": ObservationModel.model_json_schema(),
        "state": FullStateModel.model_json_schema(),
    }


@router.post("/mcp")
async def mcp(payload: dict):
    request_id = payload.get("id")
    method = payload.get("method")
    if method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "customer-support-env", "version": "1.0.0"},
            "capabilities": {},
        }
    else:
        result = {"ok": True}
    return {"jsonrpc": "2.0", "id": request_id, "result": result}

@router.post("/reset", response_model=ResetResponse)
async def reset(req: Request, request: ResetRequest | None = None):
    request = request or ResetRequest()
    session_id = req.headers.get("X-Session-Id", DEFAULT_SESSION)
    env = session_manager.create(session_id, task=request.task, seed=request.seed)
    obs = env.reset(task=request.task, seed=request.seed)
    return ResetResponse(observation=obs.model_dump(), done=False, info={})

@router.post("/step", response_model=StepResponse)
async def step(request: StepRequest, req: Request):
    session_id = req.headers.get("X-Session-Id", DEFAULT_SESSION)
    env = session_manager.get(session_id)
    if env is None: raise HTTPException(status_code=400, detail="No active session. Call /reset first.")
    try:
        action_type = ActionType(request.action_type)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid action_type '{request.action_type}'. Choose from: {[a.value for a in ActionType]}")
    action = ActionModel(action_type=action_type, content=request.content)
    result = env.step(action)
    return StepResponse(observation=result.observation.model_dump(), reward=result.reward, done=result.done, info=result.info)

@router.get("/state", response_model=StateResponse)
async def state(req: Request):
    session_id = req.headers.get("X-Session-Id", DEFAULT_SESSION)
    env = session_manager.get(session_id)
    if env is None: raise HTTPException(status_code=400, detail="No active session. Call /reset first.")
    full_state = env.state()
    return StateResponse(**full_state.model_dump())
