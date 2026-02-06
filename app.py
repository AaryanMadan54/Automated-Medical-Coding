import streamlit as st
import json
import pandas as pd
from database import SentinelDB
from vector_engine import SentinelVectorEngine
from sentinel_agent import SentinelHybridAgent

# Page Config
st.set_page_config(page_title="Sentinel AI Coder", page_icon="🏥", layout="wide")

# --- CSS Styling ---
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        font-weight: 600;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box_shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .success-score {
        color: #059669;
        font-weight: bold;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialization & Caching ---

@st.cache_resource
def load_data():
    """Loads the massive CPT dataset only once."""
    try:
        with open("cpt_hcpcs_codes.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("Using empty dataset. Run 'fetch_hf_data.py' first.")
        return []

@st.cache_resource
def init_engines(_data):
    """Initializes the heavy ML models and Database engine."""
    db = SentinelDB()
    if _data:
        # We only import if we have data, but checking if DB is empty might be better optimization
        # For now, we follow existing pattern (re-import on clean start)
        db.import_cpt_json(_data) 
    
    ve = SentinelVectorEngine()
    if _data:
        ve.index_codes(_data)
    
    agent = SentinelHybridAgent(db, ve)
    return db, ve, agent

# Load everything
with st.spinner("Initializing Sentinel AI Core..."):
    cpt_data = load_data()
    db, ve, agent = init_engines(cpt_data)

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063198.png", width=100) # Placeholder Medical Icon
    st.title("Sentinel AI")
    st.markdown("Automated Medical Coding Assistant")
    
    st.divider()
    
    st.subheader("Database Stats")
    st.write(f"📂 Total Codes: **{len(cpt_data):,}**")
    
    if st.button("Unload/Reset Database"):
        st.cache_resource.clear()
        st.rerun()

# --- Main Interface ---

st.markdown('<div class="main-header">Sentinel AI Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="sub-header">Clinical Note Input</div>', unsafe_allow_html=True)
    note_input = st.text_area(
        "Enter Doctor's Notes below for real-time coding analysis:",
        height=200,
        placeholder="e.g. Patient presents for initial evaluation of..."
    )

    if st.button("Run Analysis", type="primary", use_container_width=True):
        if not note_input.strip():
            st.warning("Please enter a clinical note first.")
        else:
            with st.spinner("Analyzing clinical documentation..."):
                report = agent.analyze_note(note_input)
                
                # --- Result Display ---
                st.success("Analysis Complete")
                
                # Top Card: Suggested Code
                st.markdown(f"""
                <div class="card">
                    <h3>📍 Suggested Code: <span style="color: #2563EB;">{report['identified_code']}</span></h3>
                    <p><b>Description:</b> {report['current_suggestion']['description']}</p>
                    <p class="success-score">Match Confidence: {report['confidence_score']}%</p>
                </div>
                """, unsafe_allow_html=True)

                # Analysis Details (The "Smart" Part)
                with st.expander("📄 Detailed Gap Analysis & Audit", expanded=True):
                    st.markdown(report['analysis'])
    
with col2:
    st.markdown('<div class="sub-header">Recent Audit Logs</div>', unsafe_allow_html=True)
    
    # Fetch logs directly from SQLite
    try:
        logs_df = pd.read_sql_query("SELECT timestamp, suggested_code, confidence FROM audit_logs ORDER BY id DESC LIMIT 5", db.conn)
        st.dataframe(logs_df, hide_index=True, use_container_width=True)
    except Exception as e:
        st.info("No audit logs available yet.")

st.divider()
st.caption("Sentinel AI v1.0 | Powered by Groq & Semantic Search")
