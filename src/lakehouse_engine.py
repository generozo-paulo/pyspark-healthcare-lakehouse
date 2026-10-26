import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, List, Dict
from src.schemas import BronzeAdmissionRecord, SilverEncounterRecord, GoldClinicalKPIs

class HealthcareLakehousePipeline:
    """
    Motor analítico simulador de arquitetura Lakehouse Medallion (Bronze -> Silver -> Gold)
    utilizando computação vetorizada equivalente aos jobs distribuídos PySpark.
    """

    SERVICES = ["Cardiologia", "Pneumologia", "Terapia Intensiva (UTI)", "Cirurgia Geral", "Neurologia"]
    ICD_CODES = ["I21.9", "J18.9", "A41.9", "K35.8", "I63.9"]

    @staticmethod
    def generate_bronze_layer(n_records: int = 5000, random_state: int = 42) -> pd.DataFrame:
        """Gera eventos brutos simulando a camada Bronze (Raw Append-Only)."""
        np.random.seed(random_state)
        base_date = datetime(2025, 1, 1)

        records = []
        for i in range(n_records):
            adm_delta = np.random.randint(0, 300)
            adm_dt = base_date + timedelta(days=int(adm_delta), hours=int(np.random.randint(0, 24)))
            los_days = float(np.random.exponential(scale=5.2) + 0.5)
            disch_dt = adm_dt + timedelta(days=los_days)

            service = str(np.random.choice(HealthcareLakehousePipeline.SERVICES))
            icd = str(np.random.choice(HealthcareLakehousePipeline.ICD_CODES))
            cost = float(np.random.normal(loc=12500, scale=4000) + (los_days * 1800))
            is_death = 1 if (np.random.rand() < 0.08 or service == "Terapia Intensiva (UTI)" and np.random.rand() < 0.18) else 0

            records.append({
                "raw_event_id": f"EVT-{i+1:06d}",
                "patient_mrn": f"MRN-{np.random.randint(1000, 2500):05d}", # pacientes recorrentes
                "admission_datetime": adm_dt.isoformat(),
                "discharge_datetime": disch_dt.isoformat(),
                "admission_type": np.random.choice(["EMERGENCY", "ELECTIVE", "URGENT"]),
                "clinical_service": service,
                "primary_icd10": icd,
                "total_cost_brl": round(max(cost, 1500.0), 2),
                "in_hospital_death": is_death
            })

        return pd.DataFrame(records)

    @staticmethod
    def process_silver_layer(bronze_df: pd.DataFrame) -> pd.DataFrame:
        """Limpeza, conformação e enriquecimento temporal (Silver Layer)."""
        df = bronze_df.copy()
        df["admission_dt"] = pd.to_datetime(df["admission_datetime"])
        df["discharge_dt"] = pd.to_datetime(df["discharge_datetime"])

        # Cálculo do tempo de permanência em dias
        df["length_of_stay_days"] = (df["discharge_dt"] - df["admission_dt"]).dt.total_seconds() / 86400.0
        df["length_of_stay_days"] = df["length_of_stay_days"].clip(lower=0.1)

        # Ordenar por paciente e admissão para detectar readmissões em 30 dias
        df = df.sort_values(by=["patient_mrn", "admission_dt"]).reset_index(drop=True)
        df["prev_discharge_dt"] = df.groupby("patient_mrn")["discharge_dt"].shift(1)
        df["days_since_prev_discharge"] = (df["admission_dt"] - df["prev_discharge_dt"]).dt.total_seconds() / 86400.0

        df["is_readmission_30d"] = df["days_since_prev_discharge"].apply(lambda x: True if pd.notnull(x) and 0.0 < x <= 30.0 else False)
        df["service_normalized"] = df["clinical_service"].str.strip().str.title()
        df["in_hospital_mortality"] = df["in_hospital_death"] == 1

        return df

    @staticmethod
    def process_gold_layer(silver_df: pd.DataFrame) -> pd.DataFrame:
        """Agregações de KPIs clínicos e financeiros para BI e Feature Store (Gold Layer)."""
        gold = silver_df.groupby("service_normalized").agg(
            total_encounters=("raw_event_id", "count"),
            mean_length_of_stay=("length_of_stay_days", "mean"),
            readmission_30d_rate=("is_readmission_30d", "mean"),
            mortality_rate=("in_hospital_mortality", "mean"),
            avg_hospital_cost=("total_cost_brl", "mean")
        ).reset_index()

        gold["mean_length_of_stay"] = gold["mean_length_of_stay"].round(2)
        gold["readmission_30d_rate"] = gold["readmission_30d_rate"].round(4)
        gold["mortality_rate"] = gold["mortality_rate"].round(4)
        gold["avg_hospital_cost"] = gold["avg_hospital_cost"].round(2)

        return gold
