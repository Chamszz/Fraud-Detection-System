import pandas as pd
import sqlite3
import os
from datetime import datetime

from config import dataPath

d = pd.read_csv(dataPath)

def parseTime(d):
    if 'trans_date_trans_time' in d.columns:
        dt = pd.to_datetime(d['trans_date_trans_time'])
    elif 'trans_time' in d.columns:
        dt = pd.to_datetime(d['trans_time'], format='%H:%M:%S', errors='coerce')
    else:
        raise KeyError('No time column')
    d['datetime'] = dt
    d['hour'] = d['datetime'].dt.hour
    d['minute'] = d['datetime'].dt.minute
    d['second'] = d['datetime'].dt.second
    d['time_value'] = d['hour'] + d['minute'] / 60.0 + d['second'] / 3600.0
    return d

def calc_age(dob):
    try:
        bd = pd.to_datetime(dob)
        today = datetime.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except:
        return None

d = parseTime(d)
grp = d.groupby('cc_num')

conn = sqlite3.connect('user_profiles.db')
c = conn.cursor()

c.execute("PRAGMA table_info(user_profiles)")
cols = [r[1] for r in c.fetchall()]
if cols != ['cc_num', 'avg_amount', 'frequent_time', 'merchant', 'first_name', 'last_name', 'gender', 'age']:
    c.execute('DROP TABLE IF EXISTS user_profiles')

c.execute('''
CREATE TABLE IF NOT EXISTS user_profiles (
    cc_num TEXT PRIMARY KEY,
    avg_amount REAL,
    frequent_time REAL,
    merchant TEXT,
    first_name TEXT,
    last_name TEXT,
    gender TEXT,
    age INTEGER
)
''')

for cc, g in grp:
    avg_amt = g['amt'].mean()
    freq_t = g['time_value'].mean()
    merch = g['merchant'].mode()[0] if not g['merchant'].mode().empty else 'Unknown'
    merch = merch.replace('fraud_', '')
    
    row = g.iloc[0]
    fname = row['first'] if 'first' in row else 'Unknown'
    lname = row['last'] if 'last' in row else 'Unknown'
    gnd = row['gender'] if 'gender' in row else 'Unknown'
    age = calc_age(row['dob']) if 'dob' in row else None
    
    c.execute('''
    INSERT OR REPLACE INTO user_profiles (cc_num, avg_amount, frequent_time, merchant, first_name, last_name, gender, age)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (str(cc), avg_amt, freq_t, merch, fname, lname, gnd, age))

conn.commit()
conn.close()

print("Profiles created")