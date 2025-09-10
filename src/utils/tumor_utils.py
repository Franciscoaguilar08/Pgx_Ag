
from typing import List, Tuple

TUMORES_VALIDOS = [
    "adenocarcinoma de pulmón", "cáncer de pulmón nsclc", "cáncer de pulmón sclc",
    "cáncer de colon", "cáncer colorectal", "cáncer de mama", "cáncer gástrico",
    "melanoma", "cáncer de próstata", "cáncer de ovario", "cáncer de tiroides",
    "cáncer de vejiga", "cáncer de riñón", "cáncer de hígado", "cáncer de páncreas",
    "cáncer de cabeza y cuello", "glioblastoma", "sarcoma", "tumores neuroendocrinos",
    "cáncer de mama hr+", "cáncer de mama her2+", "cáncer de mama triple negativo",
    "melanoma cutáneo", "melanoma uveal", "melanoma mucosal",
    "cáncer colorectal msí-h", "cáncer colorectal mss",
    "leucemia mieloide aguda (lma)", "leucemia linfoide aguda (lla)",
    "leucemia mieloide crónica (lmc)", "linfoma no-hodgkin",
    "linfoma de hodgkin", "mieloma múltiple", "síndromes mielodisplásicos",
    "linfoma difuso de células b grandes", "linfoma folicular",
    "linfoma de células del manto", "linfoma de hodgkin clásico"
]

BIOMARCADORES_POR_TUMOR = {
    "adenocarcinoma de pulmón": ["EGFR", "ALK", "KRAS", "BRAF", "ROS1", "MET", "RET", "NTRK", "PD-L1"],
    "cáncer de pulmón nsclc": ["EGFR", "ALK", "KRAS", "BRAF", "ROS1", "MET", "RET", "NTRK", "PD-L1"],
    "cáncer de colon": ["KRAS", "NRAS", "BRAF", "MSI-H", "dMMR", "HER2", "NTRK"],
    "cáncer colorectal": ["KRAS", "NRAS", "BRAF", "MSI-H", "dMMR", "HER2", "NTRK"],
    "cáncer de mama": ["HER2", "HR+", "PIK3CA", "BRCA", "PD-L1", "ESR1"],
    "cáncer de mama hr+": ["PIK3CA", "ESR1", "BRCA", "PD-L1"],
    "cáncer de mama her2+": ["HER2", "PIK3CA", "PD-L1"],
    "melanoma": ["BRAF", "NRAS", "c-KIT", "PD-L1", "TMB"],
    "cáncer gástrico": ["HER2", "MSI-H", "PD-L1", "EBV"],
    "leucemia mieloide aguda (lma)": ["FLT3", "IDH1", "IDH2", "NPM1", "TP53"],
    "linfoma no-hodgkin": ["PD-L1", "CD19", "CD20", "MYC", "BCL2"]
}

def validar_tumor(tumor_input: str) -> Tuple[bool, str, list]:
    tumor = (tumor_input or "").lower().strip()
    if not tumor:
        return False, "Debe especificar el tipo de tumor", []
    if tumor in ["tumor", "cáncer", "cancer", "neoplasia", "maligno"]:
        sugerencias = [
            "adenocarcinoma de pulmón", "cáncer de mama", "cáncer de colon",
            "melanoma", "leucemia mieloide aguda (lma)", "linfoma no-hodgkin"
        ]
        return False, "Especifique el tipo de tumor (ej: 'adenocarcinoma de pulmón')", sugerencias
    if tumor in TUMORES_VALIDOS:
        return True, "", []
    sugerencias = [t for t in TUMORES_VALIDOS if tumor in t]
    return False, f"Tumor '{tumor_input}' no válido o no encontrado.", sugerencias[:5]

def obtener_biomarcadores_sugeridos(tumor: str) -> list:
    return BIOMARCADORES_POR_TUMOR.get((tumor or "").lower().strip(), [])
