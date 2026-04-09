import sqlite3

def initFeedbackDb():
    db_path = 'transaction_feedback.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
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
    conn.commit()
    conn.close()

def logFeedback(cc_num, amt, hour, minute, second, action):
    db_path = 'transaction_feedback.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    INSERT INTO transaction_feedback (cc_num, amt, hour, minute, second, action)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(cc_num), amt, hour, minute, second, action))
    conn.commit()
    conn.close()

# this works
if __name__ == '__main__':
    initFeedbackDb()
