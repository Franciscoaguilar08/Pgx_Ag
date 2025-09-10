from typing import Any, Dict, List
import httpx
from urllib.parse import urlencode

from ..core.config import CLINVAR_EUTILS, CLINVAR_SUMMARY, NCBI_API_KEY, HTTP_TIMEOUT
from ..core.database import cache_get, cache_set

def ping() -> bool:
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as c:
            r = c.get(CLINVAR_EUTILS, params={"db":"clinvar","term":"EGFR","retmode":"json"})
            return r.status_code == 200
    except Exception:
        return False

def search_ids(term: str, retmax: int = 5) -> List[str]:
    key = f"CLINVAR::search::{term}::{retmax}"
    data, ok = cache_get("CLINVAR", key)
    if ok and data is not None:
        return data
    ids: List[str] = []
    try:
        params = {"db":"clinvar","term":term,"retmode":"json","retmax":str(retmax)}
        if NCBI_API_KEY: params["api_key"] = NCBI_API_KEY
        with httpx.Client(timeout=HTTP_TIMEOUT) as c:
            r = c.get(CLINVAR_EUTILS, params=params)
            if r.status_code == 200:
                j = r.json()
                ids = j.get("esearchresult",{}).get("idlist",[]) or []
    except Exception:
        pass
    cache_set("CLINVAR", key, ids)
    return ids

def summaries(ids: List[str]) -> List[Dict[str, Any]]:
    if not ids: return []
    key = f"CLINVAR::summary::{','.join(ids)}"
    data, ok = cache_get("CLINVAR", key)
    if ok and data is not None:
        return data
    out: List[Dict[str, Any]] = []
    try:
        params = {"db":"clinvar","retmode":"json","id":",".join(ids)}
        if NCBI_API_KEY: params["api_key"] = NCBI_API_KEY
        with httpx.Client(timeout=HTTP_TIMEOUT) as c:
            r = c.get(CLINVAR_SUMMARY, params=params)
            if r.status_code == 200:
                j = r.json()
                out = list((j.get("result") or {}).values())
    except Exception:
        pass
    cache_set("CLINVAR", key, out)
    return out

def find_variant_summary(gene: str, protein_change: str) -> List[Dict[str, Any]]:
    term = f"{gene}[gene] AND {protein_change}"
    ids = search_ids(term, 5)
    return summaries(ids)
