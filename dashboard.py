import streamlit as st
import sqlite3
import pandas as pd

# Page Config
st.set_page_config(page_title="Retention Engine Dashboard", layout="wide")

st.title("📊 Marketplace Retention Command Center")
st.markdown("Monitoring real-time churn detection and automated Braze triggers.")

# Connect to the Database created by the engine
conn = sqlite3.connect('marketplace.db')

# 1. Overview Metrics
col1, col2, col3 = st.columns(3)
users_count = pd.read_sql("SELECT COUNT(*) FROM users", conn).iloc[0,0]
churn_count = pd.read_sql("SELECT COUNT(*) FROM users WHERE status='churned'", conn).iloc[0,0]
active_count = users_count - churn_count

col1.metric("Total Users", users_count)
col2.metric("Active Users", active_count)
col3.metric("⚠️ Detected At-Risk (Churned)", churn_count, delta_color="inverse")

st.divider()

# 2. View The "At-Risk" Segment (The Logic)
st.subheader("🎯 Target Segment: High-Value Churned Users")
st.info("Logic: Last Login > 30 Days Ago AND Total Spend > $50")

# Query the same logic used in the engine
sql_query = """
SELECT id, email, last_login, total_spend, status 
FROM users 
WHERE last_login < date('now', '-30 days') 
AND total_spend > 50
"""
df_risk = pd.read_sql(sql_query, conn)

if not df_risk.empty:
    st.dataframe(df_risk, use_container_width=True)
    st.success(f"✅ Engine successfully identified {len(df_risk)} users for re-activation.")
else:
    st.write("No users fit the churn criteria right now.")

st.divider()

# 3. Full Database View
with st.expander("📂 View Full User Database"):
    df_all = pd.read_sql("SELECT * FROM users", conn)
    st.dataframe(df_all)

st.caption("Data source: local SQLite database (marketplace.db)")