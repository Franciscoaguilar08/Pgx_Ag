import json
from typing import Any, Dict, Optional
import httpx

from ..core.config import CIVIC_URL, HTTP_TIMEOUT, HTTP_RETRIES
from ..core.database import cache_get, cache_set

_GQL_VARIANT = """
query VariantEvidence($gene: String!, $variant: String!) {
  evidenceItems(geneNames: [$gene], variantNames: [$variant], page: 0, size: 5) {
    records {
      id
      evidenceType
      significance
      clinicalSignificance
      disease {
        name
      }
      drugs {
        name
      }
      description
      source {
        citation
        journal
        publicationYear
        url
      }
      evidenceLevel
    }
  }
}
"""

def _retry_client() -> httpx.Client:
    return httpx.Client(timeout=HTTP_TIMEOUT)

def ping() -> bool:
    try:
        with _retry_client() as c:
            r = c.post(CIVIC_URL, json={"query":"{ stats { genes } }"})
            return r.status_code == 200
    except Exception:
        return False

def query_variant(gene: str, protein_change: str) -> Dict[str, Any]:
    """Consulta CIViC para evidencia resumida. Usa cache y nunca rompe el flujo."""
    key = f"CIVIC::{gene}::{protein_change}"
    data, ok = cache_get("CIVIC", key)
    if ok and data:
        return data
    payload = {"query": _GQL_VARIANT, "variables": {"gene": gene, "variant": protein_change}}
    out = {"items": []}
    try:
        with _retry_client() as c:
            r = c.post(CIVIC_URL, json=payload, headers={"Content-Type": "application/json"})
            if r.status_code == 200:
                j = r.json()
                items = j.get("data",{}).get("evidenceItems",{}).get("records",[]) or []
                # Reducimos a un esquema simple
                for it in items:
                    out["items"].append({
                        "evidenceLevel": it.get("evidenceLevel"),
                        "evidenceType": it.get("evidenceType"),
                        "drugNames": [d.get("name") for d in (it.get("drugs") or []) if d.get("name")],
                        "disease": it.get("disease",{}).get("name"),
                        "year": (it.get("source") or {}).get("publicationYear"),
                        "journal": (it.get("source") or {}).get("journal"),
                        "url": (it.get("source") or {}).get("url"),
                        "desc": it.get("description"),
                        "significance": it.get("clinicalSignificance") or it.get("significance"),
                    })
    except Exception:
        # No levantamos excepción: mantenemos flujo
        pass
    cache_set("CIVIC", key, out)
    return out
