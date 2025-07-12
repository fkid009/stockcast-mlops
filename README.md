# stockcast-mlops

A fully automated MLOps pipeline for stock price prediction, built with Airflow, scikit-learn, MLflow, and Streamlit. 
It predicts the next-day closing price of a stock and serves it through an API and dashboard.

---

## Project Overview

**stockcast-mlops** is an end-to-end MLOps system that:

- Fetches daily stock price data (e.g., AAPL)
- Extracts technical indicators and features
- Trains regression models (Ridge, XGBoost)
- Tracks experiments with MLflow
- Serves predictions via a Streamlit dashboard
- Automates all tasks with Airflow

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
│     predict          │            │
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
| Database               | PostgreSQL (Docker)               |
| Dashboard              | Streamlit                              |
| Deployment CI/CD       | GitHub Actions (Planned)               |
| Cloud Migration        | AWS (RDS, S3, EC2, MWAA) (Planned)      |

---

## 📂 Folder Structure

```
stockcast-mlops/
│
├── dags/                # Airflow DAGs
├── data/                # Raw and processed data
│   ├── models/          # Trained models
│   ├── params/          # Model parameters
│   └── predictions/     # Model predictions
├── postgres-init/       # PostgreSQL initialization scripts
├── scripts/             # Python scripts for DAGs
│   ├── preprocess_stock.py
│   ├── train_model.py
│   └── streamlit_app.py
├── compose.yml          # Docker Compose configuration
├── Dockerfile           # Custom Airflow Docker image
├── requirements.txt     # Python dependencies
└── README.md
```

---

## Models & Strategy

- Daily training with Ridge and XGBoost models.
- The model with the lower RMSE is selected as the best model.
- MLflow is used for experiment logging.
- Weekly hyperparameter tuning is performed to improve model performance.

---

## Getting Started (Local)

```bash
# Clone the repo
git clone https://github.com/your-username/stockcast-mlops.git
cd stockcast-mlops

# Create .env file from .env_example and fill in the values
cp .env_example .env

# Build and run the services using Docker Compose
docker-compose up --build -d

# Access the services:
# - Airflow UI: http://localhost:8080
# - Streamlit Dashboard: http://localhost:8501
# - MLflow UI: http://localhost:5000
```

---

## Database Schema

The project uses a PostgreSQL database with the following tables:

- **stock_price**: Stores historical stock price data.
  - `date`: Timestamp of the data point.
  - `open`, `high`, `low`, `close`: Stock prices.
  - `volume`: Trading volume.
  - `dividends`, `stock_splits`: Corporate actions.
  - `ticker`: Stock ticker symbol.

- **stock_pred**: Stores model predictions.
    - `date`: Date of the prediction.
    - `ticker`: Stock ticker symbol.
    - `pred_close`: Predicted closing price.
    - `model`: The model used for the prediction.

- **stock_pred_eval**: Stores the evaluation of the predictions.
  - `date`: Date of the evaluation.
  - `ticker`: Stock ticker symbol.
  - `pred_close`: Predicted closing price.
  - `true_close`: Actual closing price.
  - `abs_error`: Absolute error between predicted and actual prices.
  - `model`: The model used for the prediction.

---

## ☁️ AWS Expansion (Planned)

| Component      | Target Service |
| -------------- | -------------- |
| PostgreSQL     | Amazon RDS     |
| MLflow Backend | S3 + EC2       |
| API & UI       | EC2 / Fargate  |
| Orchestration  | Amazon MWAA    |
| CI/CD          | GitHub Actions |

---
