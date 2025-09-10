import json, os
from typing import Any, Dict, Tuple

from ..core.config import EVIDENCE_DIR, EVIDENCE_FILES
from ..core.database import cache_get, cache_set

def load_local_evidence() -> Tuple[dict, dict]:
    """Carga evidencia local desde clinical_evidence/. Cachea y no rompe si faltan."""
    cache_key = "EVIDENCE_LOCAL::v1"
    data, ok = cache_get("EVIDENCE_LOCAL", cache_key)
    if ok and data:
        return data.get("cancer",{}), data.get("pharmgx",{})
    cancer, pharmgx = {}, {}
    try:
        cancer_path = os.path.join(EVIDENCE_DIR, EVIDENCE_FILES["cancer"])
        pharm_path = os.path.join(EVIDENCE_DIR, EVIDENCE_FILES["pharmgx"])
        if os.path.exists(cancer_path):
            with open(cancer_path, "r", encoding="utf-8") as f:
                cancer = json.load(f)
        if os.path.exists(pharm_path):
            with open(pharm_path, "r", encoding="utf-8") as f:
                pharmgx = json.load(f)
    except Exception:
        pass
    cache_set("EVIDENCE_LOCAL", cache_key, {"cancer": cancer, "pharmgx": pharmgx})
    return cancer, pharmgx

def local_actions_for_variant(gene: str, protein_change: str, tumor: str) -> list:
    """Ejemplo: mapea desde evidencia local a acciones (si existen)."""
    cancer, pharm = load_local_evidence()
    out = []
    # Estructura esperada (flexible): cancer[tumor][gene][variant] -> actions[]
    tkey = (tumor or "").lower().strip()
    try:
        node = (((cancer or {}).get(tkey) or {}).get(gene.upper()) or {}).get(protein_change.upper())
        if node and isinstance(node, dict):
            out = node.get("actions") or []
    except Exception:
        pass
    return out
