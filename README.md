# 📈 stockcast-mlops

A fully automated MLOps pipeline for stock price prediction, built with Airflow, scikit-learn, MLflow, DVC, FastAPI, and Streamlit.  
It predicts the next-day closing price of a stock and serves it through an API and dashboard — ready for AWS deployment.

---

## Project Overview

**stockcast-mlops** is an end-to-end MLOps system that:

- Fetches daily stock price data (e.g., AAPL)
- Extracts technical indicators and features
- Trains regression models (Ridge, XGBoost)
- Tracks experiments with MLflow
- Versions data and models with DVC
- Serves predictions via FastAPI
- Visualizes results with Streamlit
- Automates all tasks with Airflow
- Prepares for AWS migration (RDS, S3, EC2)

---

## Architecture

```
┌────────────────────────────────────────────┐
│              Airflow DAGs                 │
│  ┌────────────┐  ┌─────────────┐           │
│  │ fetch_data │→│ preprocess   │           │
│  └────────────┘  └─────────────┘           │
│         ↓             ↓                   │
│    train_model    evaluate_model          │
│         ↓             ↓                   │
│  check_performance_drop ─────┐            │
│         ↓                    │            │
│     save_prediction          │            │
│                              │            │
│        ┌──────────────────────────────┐   │
│        │ stock_tuning_dag (GridSearch)│◄──┘
│        └──────────────────────────────┘   │
└────────────────────────────────────────────┘
```

---

## Tech Stack

| Purpose                | Tool                                   |
| ---------------------- | -------------------------------------- |
| Workflow Orchestration | Airflow (DAGs)                         |
| Data Fetching          | yfinance                               |
| ML Models              | Ridge, XGBoost (scikit-learn, xgboost) |
| Experiment Tracking    | MLflow                                 |
| Data/Model Versioning  | DVC                                    |
| Database               | PostgreSQL (Docker, RDS)               |
| API Service            | FastAPI                                |
| Dashboard              | Streamlit                              |
| Deployment CI/CD       | GitHub Actions                         |
| Cloud Migration        | AWS (RDS, S3, EC2, MWAA)               |

---

## 📂 Folder Structure

```
stockcast-mlops/
│
├── dags/                # Airflow DAGs
├── data/                # Raw and processed data (DVC tracked)
├── models/              # Trained models (DVC tracked)
├── notebooks/           # Exploratory analysis
├── src/
│   ├── data/            # fetch_data.py, feature_engineering.py
│   ├── model/           # train_model.py, tune_model.py
│   ├── api/             # FastAPI app
│   └── dashboard/       # Streamlit app
├── docker/
│   ├── airflow/         # Airflow docker-compose config
│   └── postgres/        # PostgreSQL setup
├── dvc.yaml             # DVC pipeline
├── requirements.txt     # Python dependencies
└── README.md
```

---

## Models & Strategy

- Daily training with fixed hyperparameters (Ridge or XGBoost)
- Performance drop detection → GridSearch tuning
- MLflow experiment logging
- DVC tracks all dataset/model versions

---

## Getting Started (Local)

```bash
# Clone the repo
git clone https://github.com/your-username/stockcast-mlops.git
cd stockcast-mlops

# Create virtual environment
python -m venv venv && source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL (Docker)
docker-compose -f docker/postgres/docker-compose.yml up -d

# Initialize DVC
dvc init && dvc pull

# Run Airflow scheduler + webserver
docker-compose -f docker/airflow/docker-compose.yml up -d
```

---

## API Endpoints (FastAPI)

| Endpoint   | Method | Description                  |
| ---------- | ------ | ---------------------------- |
| `/predict` | POST   | Predict next-day price       |
| `/metrics` | GET    | Get latest model performance |
| `/health`  | GET    | API health check             |

---

## Dashboard (Streamlit)

```bash
cd src/dashboard
streamlit run app.py
```

---

## ☁️ AWS Expansion (Planned)

| Component      | Target Service |
| -------------- | -------------- |
| PostgreSQL     | Amazon RDS     |
| DVC Storage    | Amazon S3      |
| MLflow Backend | S3 + EC2       |
| API & UI       | EC2 / Fargate  |
| Orchestration  | Amazon MWAA    |
| CI/CD          | GitHub Actions |

---
