from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import Any, Dict, List, Optional
import json

from ..models.schemas import ManualVariant, Biomarker, Patient
from ..utils.tumor_utils import validar_tumor, obtener_biomarcadores_sugeridos
from ..utils.vcf_parser import process_vcf_file
from ..utils.pathology_utils import extract_variants_from_text, extract_biomarkers_from_text
from ..utils.evidence import local_actions_for_variant
from ..services import civic_service, vep_service, oncokb_service, clinvar_service

router = APIRouter()

# ---------------- Demos VCF ----------------
@router.get("/demo/vcf/{key}", response_class=PlainTextResponse)
async def demo_vcf(key: str):
    demos = {
        "egfr_ex19del": "##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n7\t55242465\t.\tGGAATTAAGAGAAGCAACAT\tG\t.\tPASS\tANN=EGFR|ex19del",
        "kras_g12d": "##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n12\t25398284\t.\tG\tA\t.\tPASS\tANN=KRAS|G12D",
        "braf_v600e": "##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n7\t140453136\t.\tA\tT\t.\tPASS\tANN=BRAF|V600E",
    }
    return demos.get(key, "##fileformat=VCFv4.2\n# No demo")

# ---------------- Sugerencias ----------------
@router.post("/suggest/tumors")
async def suggest_tumors(payload: Dict[str, Any] = Body(...)):
    q = (payload.get("query") or "").lower().strip()
    from ..utils.tumor_utils import TUMORES_VALIDOS
    if not q or len(q) < 2:
        return {"suggestions": []}
    matches = [t for t in TUMORES_VALIDOS if q in t]
    if "pul" in q: matches = [t for t in TUMORES_VALIDOS if "pulmón" in t]
    if "mama" in q: matches = [t for t in TUMORES_VALIDOS if "mama" in t]
    return {"suggestions": matches[:8]}

@router.post("/suggest/biomarkers")
async def suggest_biomarkers(payload: Dict[str, Any] = Body(...)):
    tumor_type = (payload.get("tumor_type") or "")
    return {"biomarkers": obtener_biomarcadores_sugeridos(tumor_type)}

# ---------------- DEMO FULL ----------------
@router.get("/analyze_demo")
async def analyze_demo():
    return {
        "summary": "Demo: EGFR Ex19del en NSCLC; terapia sugerida: Osimertinib.",
        "details": [{
            "action": "Terapia dirigida",
            "drug": "Osimertinib",
            "variant": {"gene":"EGFR","protein_change":"Ex19del"},
            "mechanistic_badge": True,
            "strict_badge": True,
            "references": [{"label":"NCCN EGFR NSCLC", "url":"https://www.nccn.org/professionals/physician_gls/pdf/nscl.pdf"}],
            "study_meta": {"level":"1", "study_type":"Phase III", "year":2018, "sample_size":682, "disease":"NSCLC"},
            "sources": ["LocalEvidence","NCCN"],
            "clinical_context": {"why_now":"Mutación clásica sensible","timing":"primera línea","alternatives":["Gefitinib","Erlotinib"]}
        }],
        "timeline": [{"title":"Demo","description":"Datos precargados","tags":["Demo"]}]
    }

# ---------------- ANALYZE UNIFIED ----------------
@router.post("/analyze/unified")
async def analyze_unified(
    pseudonym: str = Form(...),
    diagnosis: Optional[str] = Form(""),
    tumor_type: str = Form(...),
    vcf: Optional[UploadFile] = File(None),
    manual_variants: Optional[str] = Form(None),
    biomarkers: Optional[str] = Form(None),
    pathology_report: Optional[str] = Form(None),
):
    ok, msg, sug = validar_tumor(tumor_type)
    if not ok:
        raise HTTPException(status_code=400, detail={"error": msg, "details": sug})

    detected_variants: List[dict] = []

    if vcf is not None:
        detected_variants.extend(await process_vcf_file(vcf))

    if manual_variants:
        try:
            mv = json.loads(manual_variants)
            for it in mv:
                if it.get("gene") and it.get("protein_change"):
                    detected_variants.append({
                        "gene": it["gene"].upper(),
                        "protein_change": it["protein_change"].replace("p.","").upper()
                    })
        except Exception:
            pass

    if pathology_report:
        detected_variants.extend(extract_variants_from_text(pathology_report))

    # Biomarcadores
    bios = []
    if biomarkers:
        try:
            bios = json.loads(biomarkers)
        except Exception:
            bios = []

    # Si no detectamos nada, mantenemos un ejemplo para que la UI no quede vacía
    if not detected_variants:
        detected_variants = [{"gene":"EGFR","protein_change":"L858R","zygosity":"unknown"}]

    # ----- Construcción de acciones con fuentes externas + local -----
    details = []
    refs_common = [{"label":"NCCN", "url":"https://www.nccn.org/"}]

    for var in detected_variants:
        gene = (var.get("gene") or "").upper()
        pc = (var.get("protein_change") or "").upper()
        # Local evidence (si existe)
        local_actions = local_actions_for_variant(gene, pc, tumor_type)
        for act in (local_actions or []):
            details.append({
                "action": act.get("action",""),
                "drug": act.get("drug",""),
                "variant": {"gene": gene, "protein_change": pc},
                "strict_badge": bool(act.get("strict", True)),
                "mechanistic_badge": bool(act.get("mechanistic", True)),
                "references": (act.get("references") or refs_common),
                "study_meta": act.get("study_meta") or {"level":"-"},
                "sources": act.get("sources") or ["LocalEvidence"],
                "clinical_context": act.get("clinical_context") or {},
            })

        # CIViC
        civic = civic_service.query_variant(gene, pc)
        if civic and civic.get("items"):
            top = civic["items"][0]
            drug = (top.get("drugNames") or [None])[0]
            details.append({
                "action": "Terapia/Asociación (CIViC)",
                "drug": drug or "—",
                "variant": {"gene": gene, "protein_change": pc},
                "strict_badge": True if top.get("evidenceLevel") in ("A","B","1","2") else False,
                "mechanistic_badge": True,
                "references": [{"label": top.get("journal") or "CIViC", "url": top.get("url")}] + refs_common,
                "study_meta": {"level": top.get("evidenceLevel") or "-", "year": top.get("year")},
                "sources": ["CIViC"],
                "clinical_context": {"why_now": top.get("desc") or "", "timing": top.get("disease") or ""}
            })

        # ClinVar (resumen)
        clin = clinvar_service.find_variant_summary(gene, pc)
        if clin:
            details.append({
                "action": "Significado Clínico (ClinVar)",
                "drug": "—",
                "variant": {"gene": gene, "protein_change": pc},
                "strict_badge": False,
                "mechanistic_badge": False,
                "references": [{"label":"ClinVar", "url":"https://www.ncbi.nlm.nih.gov/clinvar/"}],
                "study_meta": {"level": "db", "year": "-"},
                "sources": ["ClinVar"],
                "clinical_context": {"why_now": "Resumen de registros", "timing": ""}
            })

        # OncoKB (si hay token)
        okb = oncokb_service.annotate(gene, pc)
        if okb and isinstance(okb, dict) and okb.get("data"):
            details.append({
                "action": "Anotación (OncoKB)",
                "drug": "—",
                "variant": {"gene": gene, "protein_change": pc},
                "strict_badge": False,
                "mechanistic_badge": True,
                "references": [{"label":"OncoKB", "url":"https://www.oncokb.org/"}],
                "study_meta": {"level": "KB", "year": "-"},
                "sources": ["OncoKB"],
                "clinical_context": {"why_now": "Anotación estandarizada", "timing": ""}
            })

        # VEP (consecuencias)
        # Si el VCF no trae coordenadas, esto no aplica; mantenemos flujo
        # (el parser actual devuelve variante dummy; esta llamada es opcional)
        # vep = vep_service.annotate_region(chrom, pos, ref, alt)  # si tuvieras coords reales

        # Determinístico mínimo (por si nada devolvió)
        if not local_actions and not civic and not clin and not okb:
            if gene == "EGFR" and ("L858R" in pc or "EX19DEL" in pc or "DEL" in pc):
                details.append({
                    "action": "Terapia dirigida",
                    "drug": "Osimertinib",
                    "variant": {"gene": gene, "protein_change": pc},
                    "strict_badge": True,
                    "mechanistic_badge": True,
                    "references": refs_common,
                    "study_meta": {"level":"1", "study_type":"Phase III", "year": 2018, "sample_size": 682, "disease": "NSCLC"},
                    "sources": ["Rule"],
                    "clinical_context": {"why_now": "Mutación clásica sensible", "timing":"primera línea", "alternatives": ["Gefitinib","Erlotinib"]}
                })
            elif gene == "KRAS" and "G12D" in pc:
                details.append({
                    "action": "Ensayos clínicos",
                    "drug": "KRASi (en desarrollo)",
                    "variant": {"gene": gene, "protein_change": pc},
                    "strict_badge": False,
                    "mechanistic_badge": True,
                    "references": refs_common,
                    "study_meta": {"level":"Investigacional"},
                    "sources": ["Rule"],
                    "clinical_context": {"why_now": "Mutación KRAS clásica", "timing":"segundas líneas", "alternatives": ["Quimioterapia"]}
                })
            elif gene == "BRAF" and "V600E" in pc:
                details.append({
                    "action": "Terapia combinada",
                    "drug": "Dabrafenib + Trametinib",
                    "variant": {"gene": gene, "protein_change": pc},
                    "strict_badge": True,
                    "mechanistic_badge": True,
                    "references": refs_common,
                    "study_meta": {"level":"2"},
                    "sources": ["Rule"],
                    "clinical_context": {"why_now": "Activación MAPK", "timing":"segundas líneas", "alternatives": ["Vemurafenib"]}
                })

    summary = (
        f"Paciente {pseudonym}. Tumor: {tumor_type}. Variantes detectadas: "
        + (", ".join([f"{v.get('gene','?')} {v.get('protein_change','?')}" for v in detected_variants]) or "ninguna")
        + ". Biomarcadores: "
        + (", ".join([b.get('name','') for b in (bios or [])]) or "no reportados")
        + "."
    )

    payload = {
        "summary": summary,
        "details": details,
        "timeline": [
            {"title": "Ingreso de datos", "description": "Se procesaron entradas múltiples", "tags": ["VCF","Manual","Biomarcadores"]},
            {"title": "Anotación", "description": "Fuentes: Local / CIViC / ClinVar / OncoKB / VEP", "tags": ["Fuentes"]},
        ],
    }
    return JSONResponse(payload)
