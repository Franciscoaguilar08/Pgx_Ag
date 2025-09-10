import os

APP_TITLE = "PGx Multi-Input · Strict + IA + Diccionario"

# -------- HTTP / Networking --------
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "18.0"))
HTTP_RETRIES = int(os.getenv("HTTP_RETRIES", "2"))

# -------- External APIs --------
CIVIC_URL = os.getenv("CIVIC_URL", "https://civicdb.org/api/graphql")
VEP_URL = os.getenv("VEP_URL", "https://rest.ensembl.org/vep/human/region")
CLINVAR_EUTILS = os.getenv("CLINVAR_EUTILS", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi")
CLINVAR_SUMMARY = os.getenv("CLINVAR_SUMMARY", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi")
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")  # opcional
CTGOV_V2 = os.getenv("CTGOV_V2", "https://clinicaltrials.gov/api/v2/studies")
ONCOKB_URL = os.getenv("ONCOKB_URL", "https://www.oncokb.org/api/v1")
ONCOKB_TOKEN = os.getenv("ONCOKB_TOKEN", "")  # recomendado

# -------- LLM (opcional) --------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE = os.getenv("OPENAI_BASE", "https://api.openai.com")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "900"))

# -------- Strict policy --------
STRICT_MODE = True  # Solo dar "strict_badge" si hay evidencia fuerte y tumor coincide

# -------- Cache --------
# Se crea en /data por defecto (persistente dentro del proyecto)
CACHE_DB = os.path.abspath(
    os.getenv("PGX_CACHE_DB")
    or os.path.join(os.path.dirname(__file__), "..", "..", "data", "pgx_cache.sqlite")
)
CACHE_TTLS = {
    "VEP": 30 * 24 * 3600,
    "CIVIC": 14 * 24 * 3600,
    "CLINVAR": 30 * 24 * 3600,
    "CTGOV": 2 * 24 * 3600,
    "ONCOKB": 14 * 24 * 3600,
    "GLOSS": 120 * 24 * 3600,
    "EVIDENCE_LOCAL": 365 * 24 * 3600,
}

# -------- Internal evidence --------
# Carpeta donde guardás tus JSON internos
EVIDENCE_DIR = os.path.abspath(
    os.getenv("PGX_EVIDENCE_DIR")
    or os.path.join(os.path.dirname(__file__), "..", "..", "clinical_evidence")
)
EVIDENCE_FILES = {
    "cancer": "cancer_evidence.json",
    "pharmgx": "pharmgx_evidence.json",
}
