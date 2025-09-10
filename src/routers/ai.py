
from fastapi import APIRouter, HTTPException, Body
from typing import Any, Dict, List
import httpx, os

from ..core.config import OPENAI_API_KEY, OPENAI_BASE, LLM_MODEL, LLM_MAX_TOKENS

router = APIRouter()

@router.post("/ai/define")
async def ai_define(payload: Dict[str, Any] = Body(...)):
    terms: List[str] = payload.get("terms") or []
    if not terms:
        raise HTTPException(status_code=400, detail="Faltan términos")
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=400, detail="IA no habilitada: configurá OPENAI_API_KEY")
    messages = [
        {"role":"system","content":"Define los términos y agrega referencias entre [1] [2] ... sin inventar."},
        {"role":"user","content":"Define: " + ", ".join(terms)}
    ]
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(f"{OPENAI_BASE}/v1/chat/completions",
                                  headers={"Authorization": f"Bearer {OPENAI_API_KEY}","Content-Type":"application/json"},
                                  json={"model": LLM_MODEL, "messages": messages, "max_tokens": LLM_MAX_TOKENS, "temperature": 0.2})
            r.raise_for_status()
            data = r.json()
            text = data.get("choices",[{}])[0].get("message",{}).get("content","")
            # return in the UI expected format
            return {"text": text, "references": [{"label":"NCCN","url":"https://www.nccn.org/"}]}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"IA HTTP error: {e}")
