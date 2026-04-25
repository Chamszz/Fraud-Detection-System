# risk stuff
riskAmt3x = 95
risk_amount_2x = 90
riskAmtScale = 25
riskTimeScale = 2
riskMlMultiplier = 200
riskThreshold = 80
riskyAmtRatio = 2.0

# db paths
dbUserProfiles = 'user_profiles.db'
dbFeedback = 'transaction_feedback.db'
dbHistory = 'transaction_history.db'

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# model and data
modelPath = os.path.join(BASE_DIR, 'models', 'model.pkl')
dataPath = os.path.join(BASE_DIR, 'data', 'creditcard.csv')

# backend url
backendUrl = 'http://localhost:8000'

# this works
