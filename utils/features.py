import sqlite3
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'user_profiles.db')

def check(cc_num):
  conn = sqlite3.connect(DB_PATH)
  cur = conn.cursor()
  cur.execute('SELECT cc_num FROM user_profiles WHERE cc_num = ?', (str(cc_num),))
  out = cur.fetchone()
  conn.close()
  if out:
    return True
  else:
    return False


def get_data(cc_num):
    conn = sqlite3.connect(DB_PATH)
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

        res = {}
        res['avg_amount'] = to_f(row[0])
        res['frequent_time'] = to_f(row[1])
        res['merchant'] = row[2]
        res['first_name'] = row[3]
        res['last_name'] = row[4]
        res['gender'] = row[5]
        res['age'] = row[6]
        return res
    else:
        return None


def process(txn):
    cc = txn['cc_num']
    amt = txn['amt']
    h = int(txn['hour'])
    m = int(txn.get('minute', 0))
    s = int(txn.get('second', 0))

    t_val = h + m / 60.0 + s / 3600.0

    base = get_data(cc)
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


# compatibility aliases
validateCreditCard = check
getUserBaseline = get_data
extractFeatures = process