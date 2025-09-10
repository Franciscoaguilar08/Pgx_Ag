
from typing import List, Dict
from fastapi import UploadFile

async def process_vcf_file(vcf: UploadFile) -> List[Dict]:
    # Minimal parser: read lines and try to find ANN or simple CHR POS REF ALT; return dummy variant
    content = (await vcf.read()).decode(errors="ignore").splitlines()
    for line in content:
        if line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 5:
            chrom, pos, _id, ref, alt = parts[:5]
            # Dummy protein change from POS/ALT length
            change = f"p.V{pos}L" if ref != alt else "p.UNKNOWN"
            return [{"gene": "EGFR", "protein_change": change, "zygosity": "unknown"}]
    # Fallback demo
    return [{"gene": "EGFR", "protein_change": "L858R", "zygosity": "unknown"}]
