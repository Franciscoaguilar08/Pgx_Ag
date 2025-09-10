from typing import Any, Dict, List
import httpx

from ..core.config import ONCOKB_URL, ONCOKB_TOKEN, HTTP_TIMEOUT
from ..core.database import cache_get, cache_set

def ping() -> bool:
    # NO rompemos si no hay token. Si hay token y responde 200 -> OK; sin token devolvemos False (chip gris/rojo).
    if not ONCOKB_TOKEN:
        return False
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as c:
            r = c.get(f"{ONCOKB_URL}/utils/info", headers={"Authorization": f"Bearer {ONCOKB_TOKEN}"})
            return r.status_code == 200
    except Exception:
        return False

def annotate(gene: str, protein_change: str) -> Dict[str, Any]:
    """Anotación básica de OncoKB por gen/aaChange. Degrada graciosamente sin token."""
    key = f"ONCOKB::{gene}::{protein_change}"
    data, ok = cache_get("ONCOKB", key)
    if ok and data:
        return data
    out: Dict[str, Any] = {"data": []}
    if not ONCOKB_TOKEN:
        cache_set("ONCOKB", key, out)
        return out
    try:
        params = {"hugoSymbol": gene, "alteration": protein_change}
        with httpx.Client(timeout=HTTP_TIMEOUT) as c:
            r = c.get(f"{ONCOKB_URL}/annotate/mutations/byGenomicChange", params=params,
                      headers={"Authorization": f"Bearer {ONCOKB_TOKEN}"})
            if r.status_code == 200:
                out = r.json()
    except Exception:
        pass
    cache_set("ONCOKB", key, out)
    return out
