#  Credit Card Fraud Detection System

> **User-Specific Fraud Detection using Random Forest with Adaptive Learning**  
> Applied Data Science Project — Python

---

##  Overview

This system detects fraudulent credit card transactions by learning each **individual user's unique spending habits** from their historical transaction data. Unlike generic fraud detectors, this model is personalized — it understands *your* transaction patterns and flags anything that deviates from your norm.

When a **high-risk or large transaction** is submitted, the system calculates a fraud risk score and presents the user with a choice: **Accept** or **Reject** the transaction. The model then **retrains itself** based on the user's decision, continuously improving its accuracy over time.

---

##  How It Works

```
User Transaction History (Dataset)
          │
          ▼
  Feature Engineering
  (amount, time, merchant category, location patterns...)
          │
          ▼
  Random Forest Classifier
  (trained on user-specific data)
          │
          ▼
  New Transaction Submitted
          │
      Risk Score
     /           \
  Low Risk      High Risk
  ✅ Auto-approve  ⚠️ Flag for review
                    │
          ┌─────────┴─────────┐
          │  User Decision     │
          │  ✅ Accept / ❌ Reject │
          └─────────┬─────────┘
                    │
          Model Retrains on Decision
          (Adaptive Learning Loop)
```

---

##  Key Features

- **User-Specific Modeling** — Each user gets their own trained model based on their personal transaction history
- **Random Forest Classifier** — Robust ensemble method that handles imbalanced fraud datasets effectively
- **Risk Scoring** — Outputs a fraud probability score for each transaction, not just a binary label
- **Adaptive Retraining** — The model learns from every Accept/Reject decision, improving with each use
- **Habit-Based Detection** — Analyzes spending patterns: time of day, transaction amount, frequency, merchant type
- **Interactive Testing** — Test any transaction amount and get an instant risk assessment with user control

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.x |
| ML Model | `scikit-learn` — RandomForestClassifier |
| Data Processing | `pandas`, `numpy` |
| Visualization | `matplotlib`, `seaborn` |
| Notebooks | Jupyter Notebook |
| Serialization | `joblib` / `pickle` |

---

## Project Structure

```
Fraud-Detection-System/
│
├── data/                    # Transaction datasets (user-specific CSV files)
├── notebooks/               # Jupyter notebooks for EDA and model training
│   ├── 01_EDA.ipynb         # Exploratory Data Analysis
│   ├── 02_Feature_Engineering.ipynb
│   └── 03_Model_Training.ipynb
│
├── src/                     # Core Python modules
│   ├── preprocess.py        # Data cleaning and feature extraction
│   ├── model.py             # Random Forest training and prediction
│   ├── risk_scorer.py       # Transaction risk scoring logic
│   └── retrain.py           # Adaptive retraining on user decisions
│
├── models/                  # Saved trained model files (.pkl)
├── visualizations/          # Output plots and charts
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Chamszz/Fraud-Detection-System.git
cd Fraud-Detection-System
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add Your Transaction Data
Place your user transaction CSV file in the `data/` folder.  
Expected columns: `transaction_id`, `amount`, `timestamp`, `merchant_category`, `label` (0=legit, 1=fraud)

### 4. Train the Model
```bash
python notebooks/train.py
```

### 5. Test a Transaction
```bash
python run_tests.py
```

Output:
```
⚠️  HIGH RISK TRANSACTION DETECTED
    Amount:      $4,500.00
    Risk Score:  87.3%
    Verdict:     Suspicious — exceeds user's typical spending pattern

    > Accept transaction? [y/n]: 
```

---

## Model Performance

| Metric | Score |
|--------|-------|
| Accuracy | ~96% |
| Precision (Fraud) | ~91% |
| Recall (Fraud) | ~89% |
| F1 Score | ~90% |
| ROC-AUC | ~0.97 |

> *Results vary based on user dataset size and transaction history length.*

---

## Adaptive Learning Loop

The system's core innovation is its **feedback-driven retraining**:

- ✅ **User accepts** a flagged transaction → added to training data as **legitimate**
- ❌ **User rejects** a flagged transaction → added to training data as **fraud**
- The model **retrains incrementally**, becoming more accurate to each user's actual behavior over time

---

## Applied Data Science Concepts Used

- Class imbalance handling (SMOTE / class weighting)
- Feature importance analysis via Random Forest
- Cross-validation and hyperparameter tuning
- Precision-Recall tradeoff optimization
- Incremental/online learning for adaptive retraining
- Exploratory Data Analysis (EDA) on financial transaction data

---

## Author

**Chamszz** — [github.com/Chamszz](https://github.com/Chamszz)  
Applied Data Science Project

---

## License

This project is for educational and research purposes.
