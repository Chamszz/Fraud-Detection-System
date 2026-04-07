import sqlite3
import math

def validateCreditCard(cc_num):
    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    cursor.execute('SELECT cc_num FROM user_profiles WHERE cc_num = ?', (str(cc_num),))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def getUserBaseline(cc_num):
    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    cursor.execute('SELECT avg_amount, frequent_time, merchant, first_name, last_name, gender, age FROM user_profiles WHERE cc_num = ?', (str(cc_num),))
    row = cursor.fetchone()
    conn.close()
    if row:
        def to_f(v):
            if isinstance(v, bytes):
                import struct
                return struct.unpack('d', v)[0]
            return float(v)
        return {
            'avg_amount': to_f(row[0]),
            'frequent_time': to_f(row[1]),
            'merchant': row[2],
            'first_name': row[3],
            'last_name': row[4],
            'gender': row[5],
            'age': row[6]
        }
    return None

def extractFeatures(txn):
    cc = txn['cc_num']
    amt = txn['amt']
    h = int(txn['hour'])
    m = int(txn.get('minute', 0))
    s = int(txn.get('second', 0))

    t_val = h + m / 60.0 + s / 3600.0

    base = getUserBaseline(cc)
    if not base:
        avg_amt = amt
        freq_t = t_val
    else:
        avg_amt = base['avg_amount']
        freq_t = base['frequent_time']

    t_raw = abs(t_val - freq_t)
    t_diff = min(t_raw, 24 - t_raw)
    t_dev = t_diff / 12.0

    a_dev = abs(amt - avg_amt) / avg_amt if avg_amt > 0 else 0.0
    a_log = math.log(amt + 1)

    return [a_dev, t_dev, a_log, t_val]