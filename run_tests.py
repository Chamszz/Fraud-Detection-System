import requests
import sqlite3
import time
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Assume backend is running on localhost:8000

# Get a sample user from DB
conn = sqlite3.connect('user_profiles.db')
cursor = conn.cursor()
cursor.execute('SELECT cc_num, avg_amount, frequent_time FROM user_profiles LIMIT 1')
row = cursor.fetchone()
conn.close()

if not row:
    print("No user profiles found. Run run_simulation.py first.")
    exit()

cc_num, avg_amount, frequent_time = row
cc_num = str(cc_num)

print(f"Testing with user {cc_num}: avg_amount={avg_amount}, frequent_time={frequent_time}")

# Test 1: Normal transaction
normal_txn = {
    "cc_num": cc_num,
    "amt": avg_amount,
    "hour": int(frequent_time),
    "minute": 0
}

print("\nTest 1: Normal transaction")
response = requests.post("http://localhost:8000/transaction", json=normal_txn)
print("Status:", response.status_code)
print("Text:", response.text)
result = response.json()
print("Response:", result)
print(f"Risk Score: {result.get('risk_score', 'N/A')}, Status: {result.get('status', 'N/A')}, Alert: {result.get('alert', 'N/A')}")
print(f"Explanation: {result.get('explanation', 'N/A')}")

# Test 2: Anomalous transaction
anomalous_amt = avg_amount * 3
anomalous_hour = int((frequent_time + 12) % 24)
anomalous_txn = {
    "cc_num": cc_num,
    "amt": anomalous_amt,
    "hour": int(anomalous_hour),
    "minute": 0
}

print("\nTest 2: Anomalous transaction")
response = requests.post("http://localhost:8000/transaction", json=anomalous_txn)
result = response.json()
print(f"Risk Score: {result['risk_score']}, Status: {result['status']}, Alert: {result['alert']}")
print(f"Explanation: {result['explanation']}")

print("\nTests completed.")