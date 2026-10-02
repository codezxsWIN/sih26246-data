#!/bin/bash

set -e

PROJECT_NAME="labour-market-intelligence"

mkdir -p "$PROJECT_NAME"/{data/{raw,interim,processed,master,exports},backend/{api,schemas,services,repositories},ml/{embeddings,skill_extraction,taxonomy,demand,supply,forecasting,shortage,explainability},pipeline/{ingestion,cleaning,normalization,aggregation,master_table},taxonomy,frontend,configs,models,tests,docs}

cd "$PROJECT_NAME"

cat > README.md <<'EOF'
# AI-Powered Labour Market Intelligence & Skill Demand-Supply Forecasting Engine

## Project Overview

A government and policymaker-focused Labour Market Intelligence (LMI) platform that analyses labour-market demand, estimates labour supply, identifies skill gaps, forecasts future demand and shortage risk, and recommends targeted skilling interventions.

The system answers:

- What jobs and skills are currently in demand?
- How strong is demand for each occupation and skill?
- How much labour supply is estimated to be available?
- Which skills have shortages or oversupply?
- Which skills are likely to become more important over the next 3, 6 and 12 months?
- Which state, district, sector, occupation or skill has the highest shortage?
- What training/skilling interventions should be prioritized?
- Why does the system predict a particular shortage?
- Can policymakers query the system using natural language?

This is NOT a traditional job portal.
This is NOT a resume screening system.
This is NOT a candidate matching system.

Core flow:

DATA SOURCES
→ DATA ENGINEERING
→ JOB & SKILL INTELLIGENCE
→ DEMAND INTELLIGENCE
→ SUPPLY ESTIMATION
→ DEMAND-SUPPLY GAP
→ FORECASTING
→ SHORTAGE RISK
→ SHAP EXPLAINABILITY
→ POLICY RECOMMENDATION
→ AI POLICY COPILOT
→ GOVERNMENT DASHBOARD

---

# Final 11-Component Intelligence Stack

## 1. Sentence-BERT (SBERT)
Type: Transformer embedding model

Purpose:
- Semantic representation of job descriptions
- Semantic representation of skills
- Occupation similarity
- Skill/taxonomy matching

Local implementation:
- Lightweight MiniLM-class embedding model
- Default local embedding service: Ollama + all-MiniLM
- Cosine similarity for semantic matching

---

## 2. Transformer NER / Skill Extractor
Type: NLP model

Purpose:
- Extract skills
- Extract occupations
- Extract qualifications
- Extract relevant entities from job descriptions

Resource-efficient strategy:

Skill dictionary
→ Regex / phrase matching
→ NER only where required
→ Embedding similarity for ambiguous cases

Do not run a heavy transformer over every record unnecessarily.

---

## 3. ARIMA
Type: Statistical time-series model

Purpose:
- Historical demand forecasting baseline
- Historical supply forecasting baseline
- Skill-demand trend baseline

Use chronological train/validation/test splitting.

Never randomly shuffle time-series data.

---

## 4. Exponential Smoothing
Type: Statistical forecasting model

Purpose:
- Lightweight forecasting baseline
- Trend/seasonality modelling
- Benchmark against ARIMA and ML forecasting

Compare:

ARIMA
vs
Exponential Smoothing
vs
XGBoost
vs
LightGBM

---

## 5. XGBoost Regressor
Type: Gradient-boosted ML model

Purpose:
Primary tabular forecasting model.

Potential features:
- Lagged demand
- Lagged supply
- Vacancy counts
- Demand growth
- Supply growth
- Vacancy growth
- Skill frequency
- Employer breadth
- Sector growth
- Training capacity
- Training completions
- Current gap
- Previous shortage ratio
- State
- District
- Sector
- Occupation
- Skill
- Month
- Quarter

Outputs:
- Future demand
- Future supply
- Future gap

Initial local configuration:
- tree_method=hist
- limited depth
- limited estimators
- early stopping
- n_jobs=2

---

## 6. LightGBM
Type: Gradient-boosted ML model

Purpose:
- Alternative forecasting model
- Benchmark against XGBoost
- Optional ensemble candidate

Compare:
- Forecast accuracy
- Training time
- Memory usage

Do not continuously run XGBoost and LightGBM simultaneously on the 8 GB machine unless required.

---

## 7. XGBoost Classifier
Type: Gradient-boosted classification model

Purpose:
Predict shortage risk.

Inputs:
- Demand growth
- Supply growth
- Current gap
- Vacancy growth
- Training capacity
- Sector growth
- Historical trends
- Forecast gap
- Shortage ratio

Outputs:

LOW
MEDIUM
HIGH
CRITICAL

---

## 8. Isotonic Regression
Type: Probability calibration

Purpose:
Calibrate shortage-risk probabilities from the XGBoost classifier.

Example:

Raw model:
0.81

Calibrated probability:
validated probability estimate

Evaluate calibration using suitable validation metrics.

---

## 9. Platt Scaling / Logistic Calibration
Type: Probability calibration

Purpose:
Alternative probability calibration method.

Compare:

Uncalibrated XGBoost
vs
Isotonic Regression
vs
Platt Scaling

Use the calibration method that performs best on validation data.

---

## 10. SHAP TreeExplainer
Type: Explainability method

Purpose:
Explain why an ML model predicts a specific shortage risk or forecast.

Example explanatory variables:
- Demand Growth
- Vacancy Growth
- Historical Gap
- Training Capacity
- Supply Growth
- Sector Growth

Example:

Shortage Risk = HIGH

Top contributing factors:
1. Demand Growth
2. Vacancy Growth
3. Historical Gap
4. Low Training Capacity
5. Supply Growth

SHAP is an explainability method, not an independent predictive model.

---

## 11. Qwen2.5 1.5B Instruct
Type: Local Large Language Model

Runtime:
Ollama

Purpose:
- AI Policy Copilot
- Natural-language question understanding
- Natural-language explanation
- Verified result summarization

The LLM MUST NOT:
- Calculate demand
- Calculate supply
- Forecast demand
- Calculate shortage
- Invent statistics
- Invent labour-market numbers
- Replace ML models

Architecture:

User Question
→ Query Understanding
→ Structured Database Query
→ Verified Results
→ RAG Context
→ Qwen2.5 1.5B
→ Natural-Language Explanation

---

# Supporting Algorithms and Systems

These are important but are not counted as additional ML models:

- Cosine Similarity
- Skill Dictionary Matching
- Regex Matching
- NCO-2015 Mapping
- Skill Taxonomy Mapping
- Weighted Demand Score
- FAISS Vector Search
- RAG
- Rule-Based Policy Engine
- Optimization / Constraints
- SQLite
- FastAPI

---

# Demand Score Engine

The Demand Score is an interpretable weighted index, NOT an ML model.

Initial weights:

| Signal | Weight |
|---|---:|
| Job Posting Volume | 30% |
| Vacancy Volume | 25% |
| Skill Frequency | 20% |
| Demand Growth | 15% |
| Employer Breadth | 10% |

Formula:

Demand Score =
0.30 × Posting Volume
+
0.25 × Vacancy Volume
+
0.20 × Skill Frequency
+
0.15 × Demand Growth
+
0.10 × Employer Breadth

All signals must be normalized before combination.

If vacancy_count is unavailable:
- DO NOT fabricate vacancy counts.
- DO NOT assume 1 posting = 1 vacancy.
- Make vacancy weighting configurable.
- Clearly display unavailable signals.

---

# Labour-Market Architecture

The platform operates at:

India
→ State
→ District
→ Sector
→ Occupation
→ Skill

For each entity expose:

- Demand
- Supply
- Gap
- Shortage Ratio
- Demand Score
- Demand Trend
- Supply Trend
- 3-Month Forecast
- 6-Month Forecast
- 12-Month Forecast
- Shortage Risk
- Confidence
- Training Capacity
- Recommendation

---

# Data Sources

## Demand Data

Preferred fields:

- job_id
- job_title
- job_description
- skills
- occupation
- sector
- company
- state
- district
- city
- posting_date
- vacancy_count
- salary
- experience
- source

## Supply Data

Preferred fields:

- state
- district
- occupation
- industry
- education
- employment_status
- labour_force
- workers
- unemployment
- technical_education

## Training Data

Preferred fields:

- state
- district
- course
- skill
- occupation
- training_provider
- training_capacity
- enrolled
- completed
- certified
- date

## Taxonomy Data

Mappings:

raw occupation
→ standardized occupation
→ NCO code

raw skill
→ canonical skill
→ skill category

## Economic/Sector Data

Potential features:

- sector
- state
- date
- employment
- industry growth
- output
- investment
- economic indicators

---

# Current Naukri Dataset Usage

Naukri-derived datasets may contain:

- Job Title
- Company
- Experience
- Package/Salary
- Location
- Skills
- Posting information
- URL

These datasets primarily support DEMAND INTELLIGENCE.

They must NOT be treated as direct labour-supply datasets.

They must NOT automatically be interpreted as a complete representation of the Indian labour market.

Preserve:

- source_dataset
- source_record_id
- ingestion_date

for data provenance.

---

# Core Data Pipeline

RAW DATA
→ Schema Detection
→ Cleaning
→ Duplicate Detection
→ Location Normalization
→ Text Cleaning
→ Skill Extraction
→ Skill Normalization
→ Occupation Mapping
→ NCO-2015 Mapping
→ Demand Aggregation
→ Master Labour-Market Table

---

# Skill Normalization

Examples:

ML
Machine Learning
Machine-Learning

→ Machine Learning

ReactJS
React.js
React JS

→ React

Every mapping should store:

- raw_skill
- canonical_skill
- similarity_score
- mapping_method
- confidence
- taxonomy_id

---

# Occupation Normalization

Examples:

Data Scientist
Data Science Specialist
Machine Learning Specialist
ML Engineer
AI Engineer

must NOT automatically be treated as one identical occupation.

Use taxonomy-based classification and preserve meaningful distinctions.

Use NCO-2015 wherever applicable.

---

# Demand-Supply Gap

Gap:

Demand - Estimated Supply

Shortage Ratio:

(Demand - Estimated Supply) / Demand

Possible categories:

- Balanced
- Moderate
- High
- Critical

Thresholds must be configurable.

Do not present arbitrary thresholds as universal economic definitions.

---

# Forecasting Architecture

Historical Labour-Market Data
→ Feature Engineering
→ Chronological Split
→ ARIMA
→ Exponential Smoothing
→ XGBoost
→ LightGBM
→ Validation
→ Selected Model
→ 3/6/12 Month Forecast

Metrics:
- MAE
- RMSE
- MAPE where appropriate

Do not use random train/test splitting for time-series forecasting.

---

# Shortage Risk Architecture

Current Gap
+
Demand Growth
+
Supply Growth
+
Vacancy Growth
+
Training Capacity
+
Sector Growth
+
Historical Trends
↓
XGBoost Classifier
↓
Raw Risk Probability
↓
Isotonic Regression / Platt Scaling
↓
LOW / MEDIUM / HIGH / CRITICAL
↓
SHAP
↓
Explanation

---

# Policy Recommendation Engine

Inputs:
- Current Demand
- Estimated Supply
- Current Gap
- Forecast Demand
- Forecast Supply
- Forecast Gap
- Shortage Risk
- Training Capacity
- Training Completion
- Sector Growth
- Location

Output:

WHERE
WHICH SKILL
HOW MUCH
WHEN

Example:

Location:
Pune, Maharashtra

Occupation:
Data Analyst

Skills:
Python
SQL
Power BI

Current:
High demand
Supply below demand

Forecast:
Projected shortage in 6 months

Training:
Capacity insufficient

Recommendation:
Evaluate expansion of relevant training capacity.

The policy engine must use verified analytical outputs.

---

# AI Policy Copilot

Example query:

"Which skills will have the highest shortage in Maharashtra IT sector in the next 6 months?"

Architecture:

Policymaker Question
→ Query Understanding
→ Structured Filter
→ Database Query
→ Verified Results
→ RAG
→ Qwen2.5 1.5B
→ Natural-Language Explanation

Important:

The LLM does NOT generate the numerical predictions.

It only explains verified outputs from the ML/statistical pipeline.

If the database does not contain sufficient evidence, the system must say that data is insufficient.

---

# Government Dashboard

## National Overview

Show:
- Total Demand
- Estimated Supply
- Total Gaps
- High-Risk Occupations
- High-Risk Skills
- Emerging Skills
- Training Capacity Indicators

## Regional Intelligence

India
→ State
→ District
→ Sector

Show:
- Demand Map
- Supply Map
- Shortage Heatmap
- Sector Trends
- High-Risk Occupations

## Occupation Intelligence

Show:
- Occupation Demand
- Occupation Supply
- Occupation Gap
- Associated Skills
- Forecast
- Risk
- SHAP Explanation

## Skill Intelligence

Show:
- Demand Score
- Skill Frequency
- Demand Growth
- Estimated Supply
- Shortage Ratio
- Forecast
- Risk Category
- Training Capacity

## Forecast Explorer

Show:
- Historical Trend
- 3-Month Forecast
- 6-Month Forecast
- 12-Month Forecast
- Confidence / Uncertainty

## Policy Recommendations

Show:
- Location
- Occupation
- Skill
- Shortage Level
- Projected Gap
- Training Capacity
- Recommendation

## AI Policy Copilot

Natural-language policy query interface.

---

# FastAPI Backend

Initial endpoints:

GET /health
GET /api/datasets
GET /api/datasets/{id}/profile
GET /api/locations
GET /api/occupations
GET /api/skills
GET /api/demand
GET /api/supply
GET /api/gaps
GET /api/forecasts
GET /api/shortage-risk
GET /api/explanations/{id}
POST /api/policy/query

Use:
- Pydantic schemas
- validation
- structured error handling
- logging
- request IDs
- API metrics

---

# Local AI Stack

Ollama:
- qwen2.5:1.5b
- all-minilm

Environment variables:

OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=qwen2.5:1.5b
EMBEDDING_MODEL=all-minilm

---

# 8 GB RAM Strategy

The prototype must run on an 8 GB RAM MacBook.

Rules:

- CPU-first
- GPU optional
- One LLM loaded at a time
- LLM concurrency = 1 initially
- Small context windows
- Small output size
- Lazy model loading
- Embedding cache enabled
- Small embedding batches
- XGBoost n_jobs=2
- No large LLM
- No local fine-tuning
- No LSTM/GRU initially
- No unnecessary microservices

Core analytical engine MUST work without the LLM.

---

# Failure / Fallback Behaviour

If Ollama unavailable:
Core analytics continue to work.

If embeddings unavailable:
Use:
- Exact skill matching
- Normalized string matching
- Taxonomy aliases

If supply data unavailable:
Display:
"Supply estimate unavailable / low confidence."

Do not fabricate supply.

If historical data insufficient:
Display:
"Insufficient historical data for reliable forecasting."

Do not generate unsupported forecasts.

If taxonomy mapping uncertain:
Store:
"Unmapped / Review Required"

---

# Explainability

Every major ML result should include:

- Prediction
- Probability
- Top features
- Feature contributions
- Human-readable explanation

For XGBoost:
Use SHAP TreeExplainer.

Example:

Shortage Risk = HIGH

Contributing factors:
1. Demand Growth
2. Vacancy Growth
3. Historical Gap
4. Low Training Capacity
5. Supply Growth

---

# Data Provenance

Every important output should be traceable.

Store:

- source_dataset
- source_record_id
- ingestion_date
- processing_version
- taxonomy_version
- model_version
- prediction_timestamp

---

# Model Evaluation

## Skill Mapping

- Precision
- Recall
- F1
- Confidence distribution

## Forecasting

- MAE
- RMSE
- MAPE where appropriate

Use chronological validation.

## Classification

- Precision
- Recall
- F1
- ROC-AUC
- Calibration Error
- Brier Score where appropriate

Do not report metrics without documented validation methodology.

---

# Recommended Directory Structure

data/
├── raw/
├── interim/
├── processed/
├── master/
└── exports/

backend/
├── api/
├── schemas/
├── services/
└── repositories/

ml/
├── embeddings/
├── skill_extraction/
├── taxonomy/
├── demand/
├── supply/
├── forecasting/
├── shortage/
└── explainability/

pipeline/
├── ingestion/
├── cleaning/
├── normalization/
├── aggregation/
└── master_table/

taxonomy/
frontend/
configs/
models/
tests/
docs/

---

# Development Phases

1. Repository and dataset audit
2. Data ingestion
3. Cleaning and normalization
4. Skill intelligence
5. Demand Score
6. Supply estimation
7. Demand-Supply Gap
8. Forecasting
9. Shortage Risk
10. Calibration + SHAP
11. Policy Engine
12. AI Policy Copilot
13. FastAPI
14. Dashboard
15. Testing and Validation

---

# Non-Negotiable Principles

1. No fabricated labour-market numbers.
2. LLM is never the numerical source of truth.
3. Demand Score is interpretable.
4. Forecasting uses time-aware validation.
5. Supply estimates report uncertainty.
6. Predictions have data provenance.
7. Core system works without LLM.
8. Local models remain lightweight.
9. No resume screening module in the core product.
10. Platform is designed for government labour-market intelligence rather than job search.

---

# Final Model Stack

1. Sentence-BERT
2. Transformer NER / Skill Extractor
3. ARIMA
4. Exponential Smoothing
5. XGBoost Regressor
6. LightGBM
7. XGBoost Classifier
8. Isotonic Regression
9. Platt Scaling
10. SHAP TreeExplainer
11. Qwen2.5 1.5B Instruct

Supporting methods:

Cosine Similarity
Skill Dictionary
NCO-2015 Mapping
Skill Taxonomy
Demand Score Weighted Index
FAISS
RAG
Rule-Based Policy Engine
Optimization / Constraints

---

# Final Architecture

LABOUR MARKET DATA
↓
DATA INGESTION
↓
DATA CLEANING & QA
↓
JOB & SKILL INTELLIGENCE
↓
DEMAND SCORE
↓
SUPPLY ESTIMATION + HISTORICAL DATA
↓
DEMAND-SUPPLY GAP
↓
ARIMA / EXPONENTIAL SMOOTHING / XGBOOST / LIGHTGBM
↓
3 / 6 / 12 MONTH FORECAST
↓
XGBOOST CLASSIFIER
↓
ISOTONIC / PLATT CALIBRATION
↓
SHAP
↓
POLICY RECOMMENDATION
↓
VERIFIED RESULTS
↓
RAG + QWEN2.5 1.5B
↓
AI POLICY COPILOT
↓
GOVERNMENT DASHBOARD
EOF

echo "Project structure created."
echo "README.md created."
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. Install Ollama and pull:"
echo "   ollama pull qwen2.5:1.5b"
echo "   ollama pull all-minilm"
echo "3. git add ."
echo "4. git commit -m 'Initial Labour Market Intelligence architecture'"
echo "5. git push"