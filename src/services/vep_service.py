from typing import Any, Dict, List
import httpx

from ..core.config import VEP_URL, HTTP_TIMEOUT
from ..core.database import cache_get, cache_set

def ping() -> bool:
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as c:
            # ping suave: OPTIONS o GET sin enviar payload pesado
            r = c.get(VEP_URL, headers={"Content-Type":"application/json", "Accept":"application/json"})
            # Algunos endpoints devuelven 400 por falta de payload; si responde, lo tomamos como vivo.
            return r.status_code in (200, 400, 405)
    except Exception:
        return False

def annotate_region(chrom: str, pos: str, ref: str, alt: str) -> Dict[str, Any]:
    """Consulta VEP para una coordenada simplificada. Cachea y no rompe flujo."""
    key = f"VEP::{chrom}:{pos}:{ref}>{alt}"
    data, ok = cache_get("VEP", key)
    if ok and data:
        return data
    out = {"transcript_consequences": []}
    try:
        payload = [{"variant": f"{chrom}:{pos}-{pos}:{ref}/{alt}"}]
        with httpx.Client(timeout=HTTP_TIMEOUT) as c:
            r = c.post(VEP_URL, json=payload, headers={"Content-Type":"application/json", "Accept":"application/json"})
            if r.status_code == 200:
                j = r.json()
                if j and isinstance(j, list):
                    out = j[0] if j else out
    except Exception:
        pass
    cache_set("VEP", key, out)
    return out
