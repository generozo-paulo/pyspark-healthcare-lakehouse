# Especificação Contratual (SDD) - PySpark Healthcare Lakehouse (Medallion Architecture)

## 1. Escopo & Objetivos
Pipeline de engenharia de dados em larga escala processando registros de internações hospitalares através do padrão Medallion Lakehouse:
- **Bronze Layer**: Ingestão bruta de eventos clínicos em formato append-only com schema imutável e timestamp de captura.
- **Silver Layer**: Limpeza, deduplicação por chave composta de paciente/episódio, tratamento de nulos e enriquecimento semântico.
- **Gold Layer**: Tabelas agregadas analíticas otimizadas para Machine Learning e BI (tempo médio de permanência - LOS, taxas de readmissão em 30 dias e mortalidade por especialidade).

## 2. Contratos de Entrada (Pydantic)

### 2.1 Evento de Admissão Bruto (`BronzeAdmissionRecord`)
- `raw_event_id`: str
- `patient_mrn`: str
- `admission_datetime`: str
- `discharge_datetime`: Optional[str] = None
- `admission_type`: str
- `clinical_service`: str
- `primary_icd10`: str
- `total_cost_brl`: float
- `in_hospital_death`: int # 0 ou 1

## 3. Contratos de Saída (Pydantic)

### 3.1 Registro Silver Sanitizado (`SilverEncounterRecord`)
- `encounter_id`: str
- `patient_mrn`: str
- `length_of_stay_days`: float
- `is_readmission_30d`: bool
- `age_group`: str
- `service_normalized`: str
- `in_hospital_mortality`: bool

### 3.2 Indicadores Agregados Gold (`GoldClinicalKPIs`)
- `clinical_service`: str
- `total_encounters`: int
- `mean_length_of_stay`: float
- `readmission_30d_rate`: float
- `mortality_rate`: float
- `avg_hospital_cost`: float
