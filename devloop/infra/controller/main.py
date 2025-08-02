"""RunPod Controller API (FastAPI)

Purpose:
1. Hide RunPod authentication from caller tools.
2. Provide a stable inference endpoint (`POST /infer`).
3. Start / stop GPU pod automatically, with idle-shutdown.

This is **Phase 1 skeleton** — networking to the actual RunPod API is
stubbed with TODOs so we can iterate quickly.
"""

from __future__ import annotations

import os
import time
import typing as t

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_TEMPLATE_ID = os.getenv("RUNPOD_TEMPLATE_ID")  # optional override

RUNPOD_API = "https://api.runpod.ai/v2"
IDLE_TIMEOUT_SEC = int(os.getenv("IDLE_TIMEOUT_SEC", "600"))  # 10 min

# runtime cache (memory only)
_STATE: dict[str, t.Any] = {
    "pod_id": None,
    "last_used": 0.0,
}

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class InferRequest(BaseModel):
    prompt: str = Field(..., example="Hello, world")
    model: str = Field("mistral:7b-instruct-q5_K_M", example="mistral:7b-instruct-q5_K_M")
    max_tokens: int | None = Field(None, example=256)


class InferResponse(BaseModel):
    output: str
    latency_ms: int


class StatusResponse(BaseModel):
    pod_id: str | None
    state: str  # e.g. RUNNING, STOPPED
    idle_seconds: int


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="DevLoop RunPod Controller", version="0.1")


@app.post("/infer", response_model=InferResponse)
async def infer(body: InferRequest):
    """Main inference endpoint used by all agents."""
    if not RUNPOD_API_KEY:
        raise HTTPException(status_code=500, detail="RUNPOD_API_KEY not configured")

    start_ts = time.perf_counter()

    # 1. Ensure pod is running
    await _ensure_pod_running()

    # 2. Forward prompt to Ollama in the pod (placeholder)
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            # NOTE: replace <pod-ip> with actual IP from _STATE (TODO)
            resp = await client.post(
                "http://<pod-ip>:11434/api/generate",
                json={
                    "model": body.model,
                    "prompt": body.prompt,
                    "options": {"temperature": 0.2, "max_tokens": body.max_tokens},
                },
            )
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}") from exc

    _STATE["last_used"] = time.time()
    latency_ms = int((time.perf_counter() - start_ts) * 1000)

    return InferResponse(output=resp.json().get("response", "<no output>"), latency_ms=latency_ms)


@app.get("/status", response_model=StatusResponse)
async def status():
    pod_id = _STATE.get("pod_id")
    state = "STOPPED" if pod_id is None else "RUNNING"  # TODO: poll RunPod
    idle = int(time.time() - _STATE.get("last_used", 0))
    return StatusResponse(pod_id=pod_id, state=state, idle_seconds=idle)


@app.post("/shutdown")
async def shutdown():
    """Manual stop (CI or human)."""
    await _stop_pod()
    return {"ok": True}


# ---------------------------------------------------------------------------
# Internal helpers (RunPod REST) — minimal stubs for now
# ---------------------------------------------------------------------------
async def _ensure_pod_running() -> None:
    if _STATE["pod_id"]:
        return  # already running

    # TODO: launch pod via RunPod API, cache IP & pod_id
    _STATE["pod_id"] = "dummy-pod-id"
    _STATE["last_used"] = time.time()


async def _stop_pod() -> None:
    if not _STATE["pod_id"]:
        return
    # TODO: send stop request to RunPod API
    _STATE["pod_id"] = None
