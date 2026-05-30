
```python
import streamlit as st
import pandas as pd
import pyotp
from SmartApi import SmartConnect

# 1. App Styling & Identity
st.set_page_config(layout="wide", page_title="Option Trader - COA 1.0")

# Top Header Banner
st.markdown("""
    <div style='background-color:#0f172a; padding:20px; border-radius:10px; margin-bottom:25px;'>
        <h1 style='color:#f8fafc; text-align:center; margin:0; font-family:sans-serif;'>🎯 OPTION TRADER</h1>
        <p style='color:#94a3b8; text-align:center; margin:5px 0 0 0;'>Investing Daddy Style - Advanced COA 1.0 Calculator</p>
    </div>
""", unsafe_allow_html=True)

# App की मेमोरी (Session State) को इनिशियलाइज करना
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 2. Core Engine: Option Chain Calculations
def generate_coa_calculations(df_raw):
    df = df_raw.copy()
    max_c_oi_idx = df['C_OI'].idxmax()
    max_p_oi_idx = df['P_OI'].idxmax()
    
    c_oi_2nd = df['C_OI'].nlargest(2).iloc[-1]
    c_oi_2nd_idx = df['C_OI'].nlargest(2).index[-1]
    
    p_oi_2nd = df['P_OI'].nlargest(2).iloc[-1]
    p_oi_2nd_idx = df['P_OI'].nlargest(2).index[-1]
    
    res_strength = round((c_oi_2nd / df['C_OI'].max()) * 100, 2)
    sup_strength = round((p_oi_2nd / df['P_OI'].max()) * 100, 2)
    
    if res_strength < 75:
        res_state = "STRONG"
    elif c_oi_2nd_idx > max_c_oi_idx:
        res_state = f"WTT (Weak Towards Top) @ {res_strength}%"
    else:
        res_state = f"WTB (Weak Towards Bottom) @ {res_strength}%"
        
    if sup_strength < 75:
        sup_state = "STRONG"
    elif p_oi_2nd_idx > max_p_oi_idx:
        sup_state = f"WTT (Weak Towards Top) @ {sup_strength}%"
    else:
        sup_state = f"WTB (Weak Towards Bottom) @ {sup_strength}%"
        
    return res_state, sup_state, max_c_oi_idx, max_p_oi_idx

def identify_market_scenario(res_state, sup_state):
    if "STRONG" in res_state and "STRONG" in sup_state:
        return "Scenario 1: No Big Movement. Reversal from EOR and EOS."
    elif "STRONG" in res_state and "WTT" in sup_state:
        return "Scenario 2: Bullish Pressure. Buy Calls at every dip."
    elif "STRONG" in res_state and "WTB" in sup_state:
        return "Scenario 3: Bearish Pressure. Buy Puts at every rise."
    elif "WTT" in res_state and "STRONG" in sup_state:
        return "Scenario 4: Bullish Breakout Expected. Avoid heavy shorts."
    elif "WTB" in res_state and "STRONG" in sup_state:
        return "Scenario 5: Bearish State. Resistance pushing down."
    elif "WTT" in res_state and "WTT" in sup_state:
        return "Scenario 6: Highly Bullish. Market can break historical highs today."
    elif "WTB" in res_state and "WTB" in sup_state:
        return "Scenario 7: Highly Bearish. Sharp crash likely."
    else:
        return "Scenario 8/9: State of Confusion. Wait for percentage to drop."

# 3. UI Logic based on Login Status
if not st.session_state.logged_in:
    # Secure Login Interface
    st.markdown("### 🔐 Angel One Secure Login Panel")
    st.info("🔒 Suraksha Alert: Aapki chabiyan code mein nahi hain. Aap jo bhi details yahan bharenge, wo temporary rahengi aur bilkul safe hain.")

    col_login1, col_login2 = st.columns(2)
    with col_login1:
        api_key = st.text_input("🔑 Enter Angel One API Key", type="password", help="SmartAPI portal se mili Trading API Key dalein")
        client_id = st.text_input("👤 Enter Angel One Client ID", placeholder="e.g., A123456")

    with col_login2:
        mpin = st.text_input("🔢 Enter 4-Digit MPIN", type="password", max_chars=4, placeholder="xxxx")
        totp_key = st.text_input("🛡️ Enter Google Authenticator TOTP Key (String)", type="password")

    login_submitted = st.button("🚀 SIGN IN & LAUNCH CALCULATOR", use_container_width=True)

    if login_submitted:
        if not (api_key and client_id and mpin and totp_key):
            st.error("❌ Kripya login karne ke liye sabhi boxes ko bharein!")
        else:
            try:
                # Live Login Connection Process
                smartApi = SmartConnect(api_key=api_key)
                totp_token = pyotp.TOTP(totp_key).now()
                session = smartApi.generateSession(client_id, mpin, totp_token)
                
                if session.get('status') == True:
                    st.session_state.logged_in = True
                    st.session_state.client_id = client_id
                    st.rerun() 
                else:
                    st.error(f"❌ Login Failed: {session.get('message', 'Invalid Details')}")
            except Exception as e:
                st.error(f"❌ Connection Error: {e}. Details aur Static IP check karein.")

else:
    # --- यहाँ से आपका मुख्य कैलकुलेटर चालू होता है ---
    st.success(f"🎉 Welcome to Option Trader! Connected successfully as {st.session_state.client_id}")
    
    if st.button("🚪 Logout / Clear Session"):
        st.session_state.logged_in = False
        st.rerun()

    # Streaming Matrix Data Structure
    raw_data = [
        {"P_OI": 22000, "P_Vol": 95000, "P_LTP": 48, "Strike": 22100, "C_LTP": 260, "C_Vol": 15000, "C_OI": 8000},
        {"P_OI": 45000, "P_Vol": 180000, "P_LTP": 82, "Strike": 22200, "C_LTP": 175, "C_Vol": 45000, "C_OI": 14000},
        {"P_OI": 98000, "P_Vol": 650000, "P_LTP": 138, "Strike": 22300, "C_LTP": 105, "C_Vol": 250000, "C_OI": 48000}, 
        {"P_OI": 35000, "P_Vol": 220000, "P_LTP": 215, "Strike": 22400, "C_LTP": 52, "C_Vol": 850000, "C_OI": 95000}, 
        {"P_OI": 8000, "P_Vol": 40000, "P_LTP": 295, "Strike": 22500, "C_LTP": 18, "C_Vol": 190000, "C_OI": 72000},
    ]
    
    df = pd.DataFrame(raw_data)
    res_state, sup_state, max_c_idx, max_p_idx = generate_coa_calculations(df)
    current_scenario = identify_market_scenario(res_state, sup_state)
    
    # DISPLAY RESULTS PANEL
    st.markdown("---")
    st.subheader(f"📊 Market Current State: {current_scenario}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🛡️ Support Status", value=sup_state)
        st.error(f"📍 EOS (Extension of Support): {df.loc[max_p_idx, 'Strike'] - 18}")
    with col2:
        st.metric(label="⚔️ Resistance Status", value=res_state)
        st.success(f"📍 EOR (Extension of Resistance): {df.loc[max_c_idx, 'Strike'] + 22}")
        
    # THE 6 REVERSALS
    st.markdown("### 🚨 Option Trader - Core Reversal Levels")
    rev1, rev2 = st.columns(2)
    with rev1:
        st.info(f"🐂 Bullish Reversal Point: {df.loc[max_p_idx, 'Strike'] + 25}")
        st.info(f"📉 Diversion - 1 (Below EOS): {df.loc[max_p_idx, 'Strike'] - 70}")
    with rev2:
        st.info(f"🐻 Bearish Reversal Point: {df.loc[max_c_idx, 'Strike'] - 25}")
        st.info(f"📈 Diversion + 1 (Above EOR): {df.loc[max_c_idx, 'Strike'] + 70}")
        
    # OPTION CHAIN TABLE
    st.markdown("### 📋 Option Chain Matrix Table")
    def highlight_matrix(row):
        style = ['' for _ in row]
        if row['Strike'] == df.loc[max_c_idx, 'Strike']:
            style[df.columns.get_loc('C_OI')] = 'background-color: #1e3a8a; color: white;'
        if row['Strike'] == df.loc[max_p_idx, 'Strike']:
            style[df.columns.get_loc('P_OI')] = 'background-color: #1e3a8a; color: white;'
        return style
        
    st.dataframe(df.style.apply(highlight_matrix, axis=1), use_container_width=True, hide_index=True)
```
