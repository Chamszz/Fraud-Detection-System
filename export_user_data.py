import sqlite3
import pandas as pd

# export report for user data

d = pd.read_csv('data/creditcard.csv')
d['cc_num'] = d['cc_num'].astype(str)

conn = sqlite3.connect('user_profiles.db')
up = pd.read_sql_query('SELECT * FROM user_profiles', conn)
conn.close()
up['cc_num'] = up['cc_num'].astype(str)

dm = d.merge(up, left_on='cc_num', right_on='cc_num', how='left')
dm['name'] = dm['first_name'] + ' ' + dm['last_name']

res = []

for cc in dm['cc_num'].unique():
  u = dm[dm['cc_num'] == cc]
  r = u.iloc[0]
  avg_amt = u['amt'].mean()
  min_amt = u['amt'].min()
  max_amt = u['amt'].max()
  risk_thresh = avg_amt * 2

  for i, row in u.iterrows():
    res.append({
      'trans_date_trans_time': row['trans_date_trans_time'],
      'cc_num': row['cc_num'],
      'name': r.get('name', 'Unknown'),
      'age': r.get('age', 'Unknown'),
      'gender': r.get('gender', 'Unknown'),
      'avg_transaction': round(avg_amt, 2),
      'lowest_transaction': round(min_amt, 2),
      'highest_transaction': round(max_amt, 2),
      'risky_threshold': round(risk_thresh, 2)
    })

# this works
out = pd.DataFrame(res)
out.to_csv('data/user_transactions_report.csv', index=False)
print('Report created: ' + str(len(out)) + ' rows')
