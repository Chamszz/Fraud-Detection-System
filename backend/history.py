import sqlite3
from datetime import datetime

db = 'transaction_history.db'

def initHistoryDb():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id TEXT PRIMARY KEY,
        cc_num TEXT,
        amt REAL,
        hour INTEGER,
        minute INTEGER,
        second INTEGER,
        risk_score INTEGER,
        status TEXT,
        timestamp DATETIME
    )
    ''')
    conn.commit()
    conn.close()

def logTransaction(tid, cc, amt, h, m, s, risk, status):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''
    INSERT OR REPLACE INTO history (id, cc_num, amt, hour, minute, second, risk_score, status, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tid, cc, amt, h, m, s, risk, status, datetime.now()))
    conn.commit()
    conn.close()

def getUserHistory(cc, limit=10):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''
    SELECT id, amt, hour, minute, second, risk_score, status, timestamp
    FROM history WHERE cc_num = ? ORDER BY timestamp DESC LIMIT ?
    ''', (cc, limit))
    rows = c.fetchall()
    conn.close()
    
    hist = []
    for r in rows:
        hist.append({
            'id': r[0],
            'amt': r[1],
            'hour': r[2],
            'minute': r[3],
            'second': r[4],
            'risk': r[5],
            'status': r[6],
            'timestamp': r[7]
        })
    return hist

def getTodaySpending(cc):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''
    SELECT SUM(amt) FROM history 
    WHERE cc_num = ? AND DATE(timestamp) = DATE('now')
    ''', (cc,))
    res = c.fetchone()
    conn.close()
    return res[0] if res[0] else 0
