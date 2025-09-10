
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ManualVariant(BaseModel):
    gene: str
    protein_change: str
    zygosity: Optional[str] = "unknown"
    allele_frequency: Optional[float] = None

class Biomarker(BaseModel):
    name: str
    value: Optional[str] = None
    status: str

class Patient(BaseModel):
    pseudonym: str
    diagnosis: Optional[str] = ""
    tumor_type: str
    biomarkers: Optional[List[str]] = []
    treatment_history: Optional[List[str]] = []
