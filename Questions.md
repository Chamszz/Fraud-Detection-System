# Project Questions and Explanation

## Tech Stack

- Python 3.x
- `scikit-learn` for machine learning (`RandomForestClassifier`)
- `pandas` and `numpy` for data processing
- `sqlite3` for lightweight local data storage
- `FastAPI` for backend APIs
- `Streamlit` for frontend user interface
- `pickle` for model serialization
- Jupyter notebook environment for model training analysis

## Topics and Concepts Used

- Supervised machine learning
- Random Forest classification
- Feature engineering
- Transaction risk scoring
- User-specific baseline modeling
- Feedback-based retraining
- REST API design
- UI interaction using Streamlit
- SQL database logging and history tracking
- Data validation and user profile lookup

## File-by-File Explanation

### `config.py`

This file stores configuration constants used across the project.

```python
riskAmt3x = 95
risk_amount_2x = 90
riskAmtScale = 25
riskTimeScale = 2
riskMlMultiplier = 200
riskThreshold = 80
riskyAmtRatio = 2.0

modelPath = 'models/model.pkl'
dataPath = 'data/creditcard.csv'
backendUrl = "http://localhost:8000"
```

Why it is used:
- Centralizes parameters so other files can import them without hard-coding values.
- Keeps path names consistent for data and model files.
- Stores business rules for risk scoring.

How it works:
- Any script imports `config.py` and references `modelPath`, `dataPath`, or thresholds.
- Changing a value here updates behavior across the project.

### `export_user_data.py`

This script creates a merged report that joins transaction data with user profile data.

```python
import pandas as pd
import sqlite3

d = pd.read_csv('data/creditcard.csv')
up = pd.read_sql_query("SELECT * FROM user_profiles", conn)

dm = d.merge(up, left_on='cc_num', right_on='cc_num', how='left')
```

Why it is used:
- Generates `data/user_transactions_report.csv` for analysis or reporting.
- Adds user metadata such as `name`, `age`, and `gender` to raw transaction rows.

How it works:
- Reads raw credit card transaction data from `data/creditcard.csv`.
- Reads user profile data from SQLite `user_profiles.db`.
- Merges the two sources and exports a consolidated CSV.

### `run_simulation.py`

This file performs sample transaction tests against the backend API.

```python
response = requests.post("http://localhost:8000/transaction", json=normal_txn)
result = response.json()
```

Why it is used:
- Validates that the backend is running and can classify transactions.
- Tests both normal and anomalous transactions.

How it works:
- Pulls a sample user from the user profile database.
- Sends a low-risk transaction and a high-risk transaction to `/transaction`.
- Prints the response and risk score.

### `run_tests.py`

This script currently is a simple REST API tester for the running backend.

Why it is used:
- Automates quick functional checks for the API endpoints.
- Helps verify model inference and response format.

How it works:
- Reads a user profile from `user_profiles.db`.
- Posts JSON transaction payloads to the backend.
- Prints the JSON response from the server.

### `backend/__init__.py`

This file is present to mark `backend/` as a Python package.

Why it is used:
- Allows `backend` modules to be imported as a package.
- No runtime code is required.

### `backend/main.py`

This is the main backend API server.

Key responsibilities:
- Loads the Random Forest model from `models/model.pkl`.
- Defines API endpoints for transaction scoring, validation, and history.
- Calculates a combined risk score using model output and business rules.
- Logs pending and approved transactions.

Important code:

```python
model_file = '../' + modelPath
with open(model_file, 'rb') as f:
    model = pickle.load(f)

fraud_prob = model.predict_proba([feat])[0][1]

risk, reason = calc_risk(fraud_prob, txn.amt, info)
```

Why it is used:
- Provides the interface the Streamlit frontend and test scripts call.
- Separates web server logic from feature extraction and model training.

How it works:
- Receives transaction payloads.
- Validates the credit card number against the user profile database.
- Extracts features from the transaction.
- Predicts fraud probability with the Random Forest model.
- Converts the probability into a risk score with threshold rules.
- Returns either `APPROVED` or `PENDING` based on risk.

### `backend/retrain.py`

This module retrains the Random Forest model using both the original dataset and user feedback.

```python
m = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
m.fit(X, y)
with open('../' + modelPath, 'wb') as f:
    pickle.dump(m, f)
```

Why it is used:
- Keeps the model updated with new labeled feedback.
- Improves detection over time based on actual user decisions.

How it works:
- Loads transaction data from `data/creditcard.csv`.
- Reads feedback from `transaction_feedback.db`.
- Appends approved transactions as legitimate examples.
- Extracts features and retrains a new Random Forest.
- Saves the retrained model back to disk.

### `backend/feedback.py`

Handles feedback database table creation and logging.

```python
c.execute('''
CREATE TABLE IF NOT EXISTS transaction_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cc_num TEXT,
    amt REAL,
    hour INTEGER,
    minute INTEGER,
    second INTEGER,
    action TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
```

Why it is used:
- Records whether a pending transaction was approved or rejected.
- Stores feedback needed for retraining.

How it works:
- Creates `transaction_feedback.db` if needed.
- Appends a new row when user action is recorded.

### `backend/history.py`

Manages transaction history logging and retrieval.

```python
c.execute('''
INSERT OR REPLACE INTO history (id, cc_num, amt, hour, minute, second, risk_score, status, timestamp)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (tid, cc, amt, h, m, s, risk, status, datetime.now()))
```

Why it is used:
- Keeps a record of transaction status and score.
- Allows users to view recent history and daily spending.

How it works:
- Saves every evaluated transaction in `transaction_history.db`.
- Returns the most recent records for a card number.
- Calculates today's spending total.

### `frontend/__init__.py`

This file is an empty package initializer.

Why it is used:
- Keeps the `frontend` folder importable as a package.
- No runtime behavior.

### `frontend/app.py`

This is the Streamlit frontend application.

Key responsibilities:
- Collects card number, amount, and transaction time from the user.
- Calls backend validation and transaction scoring.
- Displays approval or pending alerts.
- Shows a mobile-style approval screen for pending transactions.
- Loads recent transaction history.

Important code:

```python
res = requests.post(f"{backendUrl}/transaction", json=txn)
result = res.json()
```

Why it is used:
- Provides an interactive UI for managers or users.
- Makes the system easy to test without a separate frontend framework.

How it works:
- Validates user input locally in Streamlit.
- Sends requests to the FastAPI backend.
- Renders metrics and responses.
- Allows approval/rejection for suspicious transactions.

### `notebooks/__init__.py`

This file marks the `notebooks` folder as a package.

Why it is used:
- Makes the notebooks folder importable if necessary.
- No functional code.

### `notebooks/train.py`

This script trains the Random Forest model on transaction history.

```python
d = pd.read_csv(dataPath)

if 'trans_date_trans_time' in d.columns:
    d['datetime'] = pd.to_datetime(d['trans_date_trans_time'])

f_list = []
labels = []
for _, r in d.iterrows():
    t = {
        'cc_num': r['cc_num'],
        'amt': r['amt'],
        'hour': int(r['hour']),
        'minute': int(r['minute']),
        'second': int(r['second'])
    }
    f_list.append(extractFeatures(t))
    labels.append(r['is_fraud'])
```

Why it is used:
- Produces the initial `models/model.pkl` after training.
- Uses the same feature extraction pipeline as the backend.

How it works:
- Reads labeled transactions from the dataset.
- Builds features for each row.
- Trains `RandomForestClassifier` with class balance.
- Saves the model.

### `utils/__init__.py`

An empty initializer file.

Why it is used:
- Allows `utils` to be imported as a package.
- No runtime logic.

### `utils/features.py`

This module contains feature extraction, validation, and baseline lookup.

```python
def validateCreditCard(cc_num):
    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    cursor.execute('SELECT cc_num FROM user_profiles WHERE cc_num = ?', (str(cc_num),))
```

Why it is used:
- Validates whether the card exists in the system.
- Fetches user baseline statistics used for risk scoring.
- Builds the model input feature vector.

How it works:
- `validateCreditCard` checks the SQLite user profile database.
- `getUserBaseline` reads average amount and frequent time for a card.
- `extractFeatures` computes: amount deviation, time deviation, log amount, and transaction time.

### `src/`

This folder is currently empty.

Why it is mentioned:
- It appears in the workspace but has no active code.
- It may be reserved for future expansion.

### Data and Models

- `data/creditcard.csv` contains transaction rows with fraud labels.
- `models/model.pkl` stores the trained Random Forest model.
- `user_profiles.db`, `transaction_feedback.db`, and `transaction_history.db` store user baseline data, feedback, and transaction history.

## Q&A: Viva-Ready Questions and Answers

### 1. What is the core function of this project?
- Answer: It detects credit card fraud using a Random Forest classifier combined with user-specific baseline scoring and interactive feedback. The system routes suspicious transactions to a pending state and improves itself from user approvals or rejections.

### 2. Why did we choose Random Forest instead of Isolation Forest?
- Answer: The project is supervised and has labeled fraud data (`is_fraud` labels). Random Forest works well for classification problems and can learn from both legitimate and fraud examples. Isolation Forest is an unsupervised anomaly detector and is less suitable when labeled fraud examples are available.

### 3. Why is user-specific baseline modeling important?
- Answer: Different users have different normal spending patterns. A transaction that is normal for one account could be suspicious for another. User baselines allow the system to compare amount and time relative to a customer's history rather than using only global thresholds.

### 4. How does feature engineering work here?
- Answer: The model uses features computed from a transaction and user baseline:
  - `a_dev`: normalized amount deviation from average
  - `t_dev`: normalized time deviation from usual hour
  - `a_log`: logarithm of amount
  - `t_val`: transaction time as a decimal hour
  These features help the model detect unusual spending amount and timing.

### 5. What is the role of `backend/main.py`?
- Answer: It exposes the main API endpoints. It loads the trained model, validates cards, predicts fraud probability, converts it to a risk score, logs transactions, and returns approval or pending status.

### 6. Why do we add a `reason` field in risk scoring?
- Answer: The reason explains why a transaction is suspicious, such as "Amount 3x+ above average" or "Unusual transaction time." This improves transparency for users and helps justify pending decisions.

### 7. How does feedback update the model?
- Answer: When a pending transaction is approved, `backend/feedback.py` records it in `transaction_feedback.db`. Then `backend/retrain.py` includes that feedback as legitimate training data in the next model retrain cycle.

### 8. Why use SQLite databases instead of CSVs for feedback and history?
- Answer: SQLite provides reliable insertion, querying, and storage for transactional logs. It is better suited for incremental writes, history retrieval, and concurrent backend usage than repeatedly appending to CSV files.

### 9. Why is `Streamlit` used for the frontend?
- Answer: Streamlit allows rapid UI prototyping for data applications. It makes it easy to build interactive forms, show metrics, and render transaction history without writing a full frontend framework.

### 10. What are the main advantages of Random Forest here?
- Answer: It is robust to outliers, handles mixed feature scales, works well with imbalanced classes using `class_weight='balanced'`, and is easy to train and persist with `pickle`.

### 11. Why not use only risk thresholds instead of ML?
- Answer: Threshold rules alone cannot capture complex patterns across amount, time, and user behavior. Machine learning adds adaptability and better generalization to detect subtle fraud patterns.

### 12. What would be the next improvement for this system?
- Answer: Add more features such as merchant category, location, transaction velocity, and session context. Also implement a proper feedback resolution endpoint and incremental retraining pipeline.

### 13. How would you explain the model pipeline end-to-end?
- Answer: Data from `creditcard.csv` trains the Random Forest model. The API receives a transaction, validates the card, extracts features, predicts fraud probability, calculates a risk score, and returns a decision. Pending transactions can later be approved or rejected, providing feedback for retraining.

### 14. What is the difference between `notebooks/train.py` and `backend/retrain.py`?
- Answer: `notebooks/train.py` trains the initial model using historical labeled data. `backend/retrain.py` retrains the model later by combining original dataset and user feedback.

### 15. Why is feature consistency important between training and inference?
- Answer: The same feature extraction function `extractFeatures` is used in both training and inference, ensuring the model receives the same input format during prediction as it did during training.

### 16. What happens if a card is not found in `user_profiles.db`?
- Answer: The transaction is rejected by validation, because `validateCreditCard` returns `False` and the backend raises a `400` error.

### 17. Why do we use `pickle` for model storage?
- Answer: `pickle` is the standard Python serialization method for scikit-learn models. It allows the trained Random Forest object to be saved and loaded efficiently.

### 18. Why include `amount` and `time` together in features?
- Answer: Fraud often happens when both the amount and transaction time deviate from normal behavior. Combining them improves detection quality.

### 19. Why are there empty `__init__.py` files?
- Answer: They enable the Python interpreter to treat folders as packages. This makes imports from `backend`, `frontend`, `notebooks`, and `utils` work correctly.

### 20. What is one major limitation of this current implementation?
- Answer: It relies on a single feature set and a basic retraining loop. It does not yet support true online learning, distributed deployment, or a fully complete transaction approval flow in the backend.

---

This `Questions` file is designed to make your project easy to explain in a viva. It covers architecture, model choice, file responsibilities, and the reasoning behind the system design.