import pandas as pd
import pickle
import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sklearn.ensemble import RandomForestClassifier
from utils.features import extractFeatures
import numpy as np
from config import dataPath, modelPath

def retrainModel():
    d = pd.read_csv(dataPath)

    if 'trans_date_trans_time' in d.columns:
        d['datetime'] = pd.to_datetime(d['trans_date_trans_time'])
    else:
        d['datetime'] = pd.to_datetime(d['trans_time'], format='%H:%M:%S', errors='coerce')

    d['hour'] = d['datetime'].dt.hour
    d['minute'] = d['datetime'].dt.minute
    d['second'] = d['datetime'].dt.second

    d_normal = d.copy()

    try:
        conn = sqlite3.connect('transaction_feedback.db')
        c = conn.cursor()
        c.execute('SELECT cc_num, amt, hour, minute, second, action FROM transaction_feedback')
        rows = c.fetchall()
        conn.close()

        for row in rows:
            if row[5] == 'approve':
                new_row = pd.DataFrame({
                    'cc_num': [row[0]],
                    'amt': [row[1]],
                    'hour': [row[2]],
                    'minute': [row[3]],
                    'second': [row[4]],
                    'is_fraud': [0]
                })
                d_normal = pd.concat([d_normal, new_row], ignore_index=True)
    except:
        pass

    f_list = []
    labels = []
    for _, r in d_normal.iterrows():
        t = {
            'cc_num': r['cc_num'],
            'amt': r['amt'],
            'hour': int(r['hour']),
            'minute': int(r['minute']),
            'second': int(r['second'])
        }
        f_list.append(extractFeatures(t))
        labels.append(r['is_fraud'])

    X = np.array(f_list)
    y = np.array(labels)

    m = RandomForestClassifier(
        n_estimators=250,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=3,
        random_state=42,
        class_weight='balanced_subsample',
        n_jobs=-1
    )
    m.fit(X, y)

    os.makedirs(os.path.join(os.path.dirname(modelPath)), exist_ok=True)
    with open(modelPath, 'wb') as f:
        pickle.dump(m, f)
    
    return True
