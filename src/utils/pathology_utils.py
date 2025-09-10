
import re
from typing import List, Dict

def extract_variants_from_text(text: str) -> List[Dict[str, str]]:
    variants = []
    patterns = [
        r'([A-Z0-9]+)\s+(?:mutación|mutado|alteración|variante)[:\s]+([A-Za-z0-9_*delins]+)',
        r'([A-Z0-9]+)\s+([A-Z][0-9]+[A-Z*]*)',
        r'([A-Z0-9]+)\s+(?:p\.)?([A-Z][a-z]{2}[0-9]+[A-Za-z*]*)'
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            gene = match.group(1).upper()
            change = match.group(2).upper()
            if not change.startswith('P.'):
                change = f"p.{change}"
            variants.append({'gene': gene, 'protein_change': change})
    return variants

def extract_biomarkers_from_text(text: str) -> List[Dict[str, str]]:
    biomarkers = []
    text_lower = text.lower()
    patterns = {
        "MSI-H": [r"MSI[-\\s]?H", r"microsatellite instability.*high", r"MSI.*high"],
        "TMB-H": [r"TMB[-\\s]?H", r"tumor mutational burden.*high", r"high tumor mutational burden"],
        "PD-L1": [r"PD[-\\s]?L1", r"programmed death ligand 1"],
        "HRD": [r"HRD", r"homologous recombination deficiency"],
        "HER2": [r"HER2", r"ERBB2"],
        "EGFR": [r"EGFR"],
        "KRAS": [r"KRAS"],
        "BRAF": [r"BRAF"]
    }
    import re as _re
    for biomarker, pattern_list in patterns.items():
        for pattern in pattern_list:
            if _re.search(pattern, text_lower, _re.IGNORECASE):
                biomarkers.append({"name": biomarker, "status": "positive"})
                break
    m = _re.search(r"PD[-\\s]?L1.*?([0-9]+)%", text, _re.IGNORECASE)
    if m:
        for b in biomarkers:
            if b["name"] == "PD-L1":
                b["value"] = f"{m.group(1)}%"
                break
    return biomarkers
