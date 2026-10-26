from pydantic import BaseModel, Field
from typing import Optional, List

class BronzeAdmissionRecord(BaseModel):
    raw_event_id: str
    patient_mrn: str
    admission_datetime: str
    discharge_datetime: Optional[str] = None
    admission_type: str
    clinical_service: str
    primary_icd10: str
    total_cost_brl: float
    in_hospital_death: int

class SilverEncounterRecord(BaseModel):
    encounter_id: str
    patient_mrn: str
    length_of_stay_days: float
    is_readmission_30d: bool
    service_normalized: str
    in_hospital_mortality: bool

class GoldClinicalKPIs(BaseModel):
    clinical_service: str
    total_encounters: int
    mean_length_of_stay: float
    readmission_30d_rate: float
    mortality_rate: float
    avg_hospital_cost: float
