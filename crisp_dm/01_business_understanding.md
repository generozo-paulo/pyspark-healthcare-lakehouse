# CRISP-DM: Entendimento de Negócio e Dados (Lakehouse Architecture)

## 1. Problema de Big Data Hospitalar
Redes de hospitais geram dezenas de milhões de eventos por mês em prontuários eletrônicos (EHR), sistemas laboratoriais (LIS) e sistemas de faturamento (ERP).
Tentar alimentar modelos preditivos e painéis de liderança diretamente dos bancos transacionais causa gargalos críticos de concorrência e inconsistência de dados.

## 2. Padrão Arquitetural Medallion
- **Bronze**: Dados crus e históricos preservados para auditoria regulatória e compliance LGPD/HIPAA.
- **Silver**: Visão única do paciente conformada, enriquecida com cálculo de tempo de permanência e flag de readmissão.
- **Gold**: Modelos analíticos dimensionais de alta performance para feature stores e tomada de decisão executiva.
