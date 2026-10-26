import streamlit as st
import pandas as pd
import plotly.express as px
from src.lakehouse_engine import HealthcareLakehousePipeline

st.set_page_config(
    page_title="Healthcare Medallion Lakehouse Dashboard",
    page_icon="🌊",
    layout="wide"
)

st.title("🌊 PySpark Healthcare Lakehouse (Medallion Architecture)")
st.markdown("""
Arquitetura de dados moderna em saúde processando eventos de internações através dos estágios **Bronze (Raw Append-Only)**, **Silver (Conformed & Enriched)** e **Gold (Executive KPIs & Feature Store)**.
""")

tab_gold, tab_silver, tab_bronze = st.tabs(["🥇 Camada Gold (KPIs Executivos & ML)", "🥈 Camada Silver (Enriquecida)", "🥉 Camada Bronze (Raw Ingest)"])

@st.cache_data
def load_data():
    bronze = HealthcareLakehousePipeline.generate_bronze_layer(n_records=3000)
    silver = HealthcareLakehousePipeline.process_silver_layer(bronze)
    gold = HealthcareLakehousePipeline.process_gold_layer(silver)
    return bronze, silver, gold

bronze_df, silver_df, gold_df = load_data()

with tab_gold:
    st.subheader("Painel Executivo de Eficiência Clínica e Desfechos (Gold Layer)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Internações", f"{len(silver_df):,}")
    c2.metric("Tempo Médio de Permanência (LOS)", f"{silver_df['length_of_stay_days'].mean():.1f} dias")
    c3.metric("Taxa Global de Readmissão 30d", f"{silver_df['is_readmission_30d'].mean():.2%}")
    c4.metric("Mortalidade Hospitalar Global", f"{silver_df['in_hospital_mortality'].mean():.2%}")

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig1 = px.bar(
            gold_df,
            x="service_normalized",
            y="readmission_30d_rate",
            title="Taxa de Readmissão em 30 Dias por Especialidade",
            color="readmission_30d_rate",
            color_continuous_scale="Reds",
            labels={"readmission_30d_rate": "Taxa de Readmissão", "service_normalized": "Especialidade"}
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        fig2 = px.scatter(
            gold_df,
            x="mean_length_of_stay",
            y="avg_hospital_cost",
            size="total_encounters",
            color="service_normalized",
            title="Relação Custo Médio vs. Tempo de Permanência (LOS)",
            labels={"mean_length_of_stay": "LOS Médio (Dias)", "avg_hospital_cost": "Custo Médio (R$)"}
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Tabela Dimensional Agregada (Gold Spec)")
    st.dataframe(gold_df, use_container_width=True)

with tab_silver:
    st.subheader("Registros Sanitizados e Enriquecidos (Silver Layer)")
    st.markdown("Visão unificada por episódio com features calculadas (LOS, Readmissão 30d e flags binárias):")
    st.dataframe(silver_df[["patient_mrn", "clinical_service", "admission_dt", "discharge_dt", "length_of_stay_days", "is_readmission_30d", "in_hospital_mortality"]].head(100), use_container_width=True)

with tab_bronze:
    st.subheader("Eventos Brutos Ingeridos (Bronze Layer)")
    st.markdown("Logs imutáveis de ingestão de telemetria hospitalar (EHR/ERP raw logs):")
    st.dataframe(bronze_df.head(100), use_container_width=True)
