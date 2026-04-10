import streamlit as st
import requests

try:
    from config import backendUrl
except ImportError:
    backendUrl = "http://localhost:8000"

st.set_page_config(page_title="Fraud Detection", layout="wide")
st.title("Credit Card Fraud Detection")

def fmtTime(h, m=0, s=0):
    p = "AM" if h < 12 else "PM"
    dh = h % 12
    if dh == 0:
        dh = 12
    return f"{dh}:{m:02d}:{s:02d} {p}"

# this works
t1, t2, t3 = st.tabs(["Terminal", "Mobile App", "History"])

with t1:
    st.header("Card Swipe")
    
    cc = st.text_input("Card Number", value="", key="cc")
    
    valid = False
    merchant = "Unknown"
    fname = "Unknown"
    lname = "Unknown"
    gender = "Unknown"
    age = None
    
    if cc:
        try:
            r = requests.get(f"{backendUrl}/validate/{cc}")
            if r.status_code == 200:
                info = r.json()
                valid = info.get('valid', False)
                merchant = info.get('merchant', 'Unknown')
                fname = info.get('first_name', 'Unknown')
                lname = info.get('last_name', 'Unknown')
                gender = info.get('gender', 'Unknown')
                age = info.get('age', None)
            else:
                valid = False
        except:
            valid = False
    
    if cc and not valid:
        st.error(f"Invalid card: {cc}")
    elif cc and valid:
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"{fname} {lname}")
            st.caption(f"Gender: {gender} | Age: {age}")
        with col2:
            st.info(f"Merchant: {merchant}")
    
    amt = st.text_input("Amount", value="")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        h = st.text_input("Hour", value="")
    with c2:
        m = st.text_input("Minute", value="")
    with c3:
        s = st.text_input("Second", value="")

    if st.button("Continue", disabled=not valid, use_container_width=True):
        errors = []
        if not cc:
            errors.append("Please enter the card number.")
        if not amt:
            errors.append("Please enter the amount.")
        elif not amt.replace('.', '').isdigit():
            errors.append("Please enter a valid amount (numeric).")
        else:
            amt_val = float(amt)
            if amt_val <= 0:
                errors.append("Please enter a positive amount.")
        if not h:
            errors.append("Please enter the hour.")
        elif not h.isdigit() or not (0 <= int(h) <= 23):
            errors.append("Please enter a valid hour (0-23).")
        if not m:
            errors.append("Please enter the minute.")
        elif not m.isdigit() or not (0 <= int(m) <= 59):
            errors.append("Please enter a valid minute (0-59).")
        if not s:
            errors.append("Please enter the second.")
        elif not s.isdigit() or not (0 <= int(s) <= 59):
            errors.append("Please enter a valid second (0-59).")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            txn = {
                "cc_num": cc,
                "amt": float(amt),
                "hour": int(h),
                "minute": int(m),
                "second": int(s)
            }

            try:
                res = requests.post(f"{backendUrl}/transaction", json=txn)
                result = res.json()

                st.subheader("Result")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", result['status'])
                with col2:
                    st.metric("Risk", result['risk_score'])
                with col3:
                    st.metric("Time", fmtTime(int(h), int(m), int(s)))
                
                st.write(f"Merchant: {result.get('merchant', 'Unknown')}")
                st.write(f"Amount: ${float(amt):.2f}")

                if result['status'] == "PENDING":
                    st.warning(f"Reason: {result['reason']}")
                    st.session_state['tid'] = result['transaction_id']
                    st.session_state['reason'] = result['reason']
                    st.session_state['amt'] = float(amt)
                    st.session_state['mrch'] = result.get('merchant', 'Unknown')
                    st.session_state['h'] = int(h)
                    st.session_state['m'] = int(m)
                    st.session_state['s'] = int(s)
                else:
                    st.success("Transaction Approved!")

            except Exception as e:
                st.error(f"Error: {str(e)}")

with t2:
    st.header("Mobile Approval")
    
    if 'tid' in st.session_state:
        st.warning("Suspicious Transaction!")
        st.write(f"Merchant: {st.session_state.get('mrch', 'Unknown')}")
        st.write(f"Amount: ${st.session_state.get('amt', 0):.2f}")
        st.write(f"Time: {fmtTime(st.session_state['h'], st.session_state['m'], st.session_state['s'])}")
        st.write(f"Reason: {st.session_state.get('reason', '')}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve", use_container_width=True):
                try:
                    res = requests.post(
                        f"{backendUrl}/transaction/{st.session_state['tid']}/resolve",
                        json={"action": "approve"}
                    )
                    st.success("Transaction approved!")
                    del st.session_state['tid']
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("Reject", use_container_width=True):
                try:
                    res = requests.post(
                        f"{backendUrl}/transaction/{st.session_state['tid']}/resolve",
                        json={"action": "reject"}
                    )
                    st.error("Transaction rejected!")
                    del st.session_state['tid']
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("No pending transactions.")

with t3:
    st.header("Transaction History")
    
    cc_hist = st.text_input("Card Number for History", value="", key="cc_hist")
    
    if cc_hist and st.button("Load History"):
        try:
            res = requests.get(f"{backendUrl}/history/{cc_hist}")
            if res.status_code == 200:
                data = res.json()
                today = data.get('today_spending', 0)
                st.metric("Today's Spending", f"${today:.2f}")
                
                hist = data.get('history', [])
                if hist:
                    st.write("Recent Transactions:")
                    for t in hist:
                        with st.container(border=True):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.write(f"Amount: ${t['amt']:.2f}")
                            with c2:
                                st.write(f"Risk: {t['risk']}")
                            with c3:
                                st.write(f"Status: {t['status']}")
                            st.caption(f"Time: {fmtTime(t['hour'], t['minute'], t['second'])}")
                else:
                    st.info("No transaction history")
            else:
                st.error("Card not found")
        except Exception as e:
            st.error(f"Error: {str(e)}")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                st.error(f"Invalid card: {e.response.json().get('detail', 'Card not found in system.')}")
            else:
                st.error(f"Error: {e.response.json().get('detail', str(e))}")
        except Exception as e:
            st.error(f"Error: {e}")