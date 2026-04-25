from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import pickle
import os
import sys
import uuid
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.features import extractFeatures, getUserBaseline, validateCreditCard
from backend.feedback import initFeedbackDb, logFeedback
from backend.retrain import retrainModel
from backend.history import initHistoryDb, logTransaction, getUserHistory, getTodaySpending
from config import *

# idk just works
app = FastAPI()

initFeedbackDb()
initHistoryDb()

model_file = modelPath
with open(model_file, 'rb') as f:
    model = pickle.load(f)

print("Model loaded successfully")

pending = {}
model_lock = threading.Lock()

def reloadModelInBackground():
    """Reload model from disk in a thread-safe way"""
    global model
    import time
    time.sleep(0.1)  # Small delay to ensure file is written
    try:
        with model_lock:
            with open(model_file, 'rb') as f:
                model = pickle.load(f)
    except Exception as e:
        print(f"Error reloading model: {e}")

class Txn(BaseModel):
    cc_num: str
    amt: float
    hour: int
    minute: int = 0
    second: int = 0

class Act(BaseModel):
    action: str

def fmtTime(h: int, m: int = 0, s: int = 0) -> str:
    p = "AM" if h < 12 else "PM"
    dh = h % 12
    if dh == 0:
        dh = 12
    return f"{dh}:{m:02d}:{s:02d} {p}"

# not sure why but dont touch
def calc_risk(fraud_prob, amt, baseline):
    risk = fraud_prob * 100  # RF prob to 0-100 scale
    reason = ""
    
    if baseline:
        ratio = amt / baseline['avg_amount'] if baseline['avg_amount'] > 0 else 1.0
        t_val = baseline.get('frequent_time', 0)
        t_raw = abs((0 - t_val))
        t_diff = min(t_raw, 24 - t_raw)
        
        if ratio >= 3:
            risk = max(risk, riskAmt3x)
            reason += "Amount 3x+ above average. "
        elif ratio >= 2:
            risk = max(risk, risk_amount_2x)
            reason += "Amount 2x+ above average. "
        elif ratio > 1:
            risk = min(100, risk + int((ratio - 1.0) * riskAmtScale))
        
        risk = min(100, risk + int(t_diff * riskTimeScale))
        if t_diff > 1.0:
            reason += "Unusual transaction time. "
    
    return int(risk), reason.strip() if reason else "Flagged by system"

@app.get("/validate/{cc_num}")
async def validate(cc_num: str):
    if not validateCreditCard(cc_num):
        return {"valid": False}
    
    info = getUserBaseline(cc_num)
    if not info:
        return {"valid": False}
    
    return {
        "valid": True,
        "merchant": info.get('merchant', 'Unknown'),
        "first_name": info.get('first_name', 'Unknown'),
        "last_name": info.get('last_name', 'Unknown'),
        "gender": info.get('gender', 'Unknown'),
        "age": info.get('age', None)
    }

@app.post("/transaction")
async def process(txn: Txn):
    if not validateCreditCard(txn.cc_num):
        raise HTTPException(status_code=400, detail="Card not in system")
    
    try:
        feat = extractFeatures(txn.dict())
        fraud_prob = model.predict_proba([feat])[0][1]
        
        info = getUserBaseline(txn.cc_num)
        risk, reason = calc_risk(fraud_prob, txn.amt, info)
        merchant = info.get('merchant', 'Unknown') if info else 'Unknown'
        
        if risk < riskThreshold:
            tid = str(uuid.uuid4())
            logTransaction(tid, txn.cc_num, txn.amt, txn.hour, txn.minute, txn.second, risk, "APPROVED")
            return {
                "status": "APPROVED",
                "transaction_id": tid,
                "risk_score": risk,
                "merchant": merchant,
                "time": fmtTime(txn.hour, txn.minute, txn.second)
            }
        
        tid = str(uuid.uuid4())
        pending[tid] = {
            'txn': txn.dict(),
            'risk': risk,
            'reason': reason,
            'merchant': merchant
        }
        
        logTransaction(tid, txn.cc_num, txn.amt, txn.hour, txn.minute, txn.second, risk, "PENDING")
        
        return {
            "status": "PENDING",
            "transaction_id": tid,
            "risk_score": risk,
            "reason": reason,
            "merchant": merchant,
            "time": fmtTime(txn.hour, txn.minute, txn.second)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")

@app.post("/transaction/{tid}/resolve")
async def resolve(tid: str, act: Act, background_tasks: BackgroundTasks):
    if tid not in pending:
        raise HTTPException(status_code=404, detail="Transaction not found")

    p = pending[tid]
    t = p['txn']
    if act.action == "approve":
        status_str = "APPROVED"
    else:
        status_str = "REJECTED"

    pending[tid]['status'] = status_str

    logFeedback(t['cc_num'], t['amt'], t['hour'], t['minute'], t['second'], act.action)
    logTransaction(tid, t['cc_num'], t['amt'], t['hour'], t['minute'], t['second'], p['risk'], status_str)

    background_tasks.add_task(retrainModel)
    background_tasks.add_task(reloadModelInBackground)

    return {
        "transaction_id": tid,
        "status": status_str,
        "message": "Feedback recorded"
    }

@app.get("/history/{cc_num}")
async def get_hist(cc_num: str):
    if not validateCreditCard(cc_num):
        raise HTTPException(status_code=400, detail="Invalid card")
    
    hist = getUserHistory(cc_num, 5)
    today_amt = getTodaySpending(cc_num)
    
    return {
        "history": hist,
        "today_spending": round(today_amt, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
