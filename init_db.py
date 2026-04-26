"""
Initialize the user_profiles database from creditcard.csv
"""
import sqlite3
import pandas as pd
import os
from datetime import datetime
from config import dataPath

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'user_profiles.db')

def calculate_age(dob_str):
    """Calculate age from date of birth string (YYYY-MM-DD)"""
    try:
        dob = pd.to_datetime(dob_str)
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return int(age)
    except:
        return 0

def init_user_profiles_db():
    """Create and populate user_profiles table from creditcard.csv"""
    
    # Read the credit card data
    df = pd.read_csv(dataPath)
    
    # Ensure cc_num is string
    df['cc_num'] = df['cc_num'].astype(str)
    
    # Get unique users with their profile data
    user_profiles = []
    
    for cc_num in df['cc_num'].unique():
        user_txns = df[df['cc_num'] == cc_num]
        first_txn = user_txns.iloc[0]
        
        # Calculate user baseline metrics
        avg_amount = user_txns['amt'].mean()
        
        # Extract hour from transaction time if available
        if 'trans_date_trans_time' in df.columns:
            df_temp = user_txns.copy()
            df_temp['datetime'] = pd.to_datetime(df_temp['trans_date_trans_time'])
            hours = df_temp['datetime'].dt.hour
            frequent_time = hours.mode()[0] if len(hours.mode()) > 0 else hours.mean()
        elif 'hour' in df.columns:
            frequent_time = user_txns['hour'].mode()[0] if len(user_txns['hour'].mode()) > 0 else user_txns['hour'].mean()
        else:
            frequent_time = 12
        
        # Get merchant if available
        merchant = str(first_txn.get('merchant', 'Unknown')) if 'merchant' in df.columns else 'Unknown'
        
        # Get personal info - use 'first' and 'last' column names
        first_name = str(first_txn.get('first', 'Unknown')) if 'first' in df.columns else 'Unknown'
        last_name = str(first_txn.get('last', 'Unknown')) if 'last' in df.columns else 'Unknown'
        gender = str(first_txn.get('gender', 'Unknown')) if 'gender' in df.columns else 'Unknown'
        
        # Calculate age from date of birth
        age = 0
        if 'dob' in df.columns:
            age = calculate_age(first_txn['dob'])
        elif 'age' in df.columns:
            age = int(first_txn.get('age', 0))
        
        user_profiles.append({
            'cc_num': str(cc_num),
            'avg_amount': float(avg_amount),
            'frequent_time': float(frequent_time),
            'merchant': merchant,
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender,
            'age': age
        })
    
    # Create database and table
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing table if it exists
    cursor.execute('DROP TABLE IF EXISTS user_profiles')
    
    # Create user_profiles table
    cursor.execute('''
        CREATE TABLE user_profiles (
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
    
    # Insert user profiles
    for profile in user_profiles:
        cursor.execute('''
            INSERT INTO user_profiles 
            (cc_num, avg_amount, frequent_time, merchant, first_name, last_name, gender, age)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile['cc_num'],
            profile['avg_amount'],
            profile['frequent_time'],
            profile['merchant'],
            profile['first_name'],
            profile['last_name'],
            profile['gender'],
            profile['age']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized: {DB_PATH}")
    print(f"Created {len(user_profiles)} user profiles")

if __name__ == '__main__':
    init_user_profiles_db()
