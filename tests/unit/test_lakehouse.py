import pytest
from src.lakehouse_engine import HealthcareLakehousePipeline

def test_bronze_layer_generation():
    bronze = HealthcareLakehousePipeline.generate_bronze_layer(n_records=100)
    assert len(bronze) == 100
    assert "raw_event_id" in bronze.columns
    assert "total_cost_brl" in bronze.columns

def test_silver_layer_processing():
    bronze = HealthcareLakehousePipeline.generate_bronze_layer(n_records=200)
    silver = HealthcareLakehousePipeline.process_silver_layer(bronze)
    assert len(silver) == 200
    assert "length_of_stay_days" in silver.columns
    assert "is_readmission_30d" in silver.columns
    assert (silver["length_of_stay_days"] > 0).all()

def test_gold_layer_aggregation():
    bronze = HealthcareLakehousePipeline.generate_bronze_layer(n_records=300)
    silver = HealthcareLakehousePipeline.process_silver_layer(bronze)
    gold = HealthcareLakehousePipeline.process_gold_layer(silver)
    assert len(gold) > 0
    assert "mean_length_of_stay" in gold.columns
    assert "readmission_30d_rate" in gold.columns
    assert (gold["readmission_30d_rate"] >= 0.0).all()
    assert (gold["mortality_rate"] >= 0.0).all()
