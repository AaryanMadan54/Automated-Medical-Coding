import json
from database import SentinelDB
from vector_engine import SentinelVectorEngine
from sentinel_agent import SentinelHybridAgent

# 1. Setup Data - Loading Hugging Face Dataset (atta00/cpt-hcpcs-codes)
try:
    with open("cpt_hcpcs_codes.json", "r") as f:
        real_cpt_json = json.load(f)
    print(f"Loaded {len(real_cpt_json)} codes from Hugging Face Dataset.")
except FileNotFoundError:
    print("JSON file not found. Please run fetch_hf_data.py first.")
    real_cpt_json = []

# 2. Initialize Engines
db = SentinelDB()
if real_cpt_json:
    db.import_cpt_json(real_cpt_json)

ve = SentinelVectorEngine()
if real_cpt_json:
    ve.index_codes(real_cpt_json)

agent = SentinelHybridAgent(db, ve)

# 3. Test a Real Clinical Note (Related to Clinical Lab services now available)
clinical_note = "Patient here for worsening knee pain and new onset of back pain. Gave a steroid injection in the left knee. Patient was in the office for about 25 minutes total. Follow up as needed."
"""
    Patient here for follow-up on Type 2 Diabetes. Reviewed glucose logs. Adjusted Metformin dose.
    Patient here for 3-month follow-up of hypertension. BP is stable at 130/80. Patient compliant with Lisinopril. No side effects reported. Heart rate regular. Plan: Continue current meds, return in 3 months.
    Patient here for worsening knee pain and new onset of back pain. Gave a steroid injection in the left knee. Patient was in the office for about 25 minutes total. Follow up as needed.
    Patient here for removal of two skin tags on the neck. Areas numbed with lidocaine. Tags removed via cryosurgery. No complications. Patient advised on wound care.
"""


if real_cpt_json:
    report = agent.analyze_note(clinical_note)

    print("\n--- SENTINEL AI ANALYSIS (REAL 2026 DATA) ---")
    print(f"\nSUGGESTED: {report['identified_code']} ({report['confidence_score']}% Match)")
    print("\n" + "="*50)
    print(report['analysis'])
else:
    print("No data loaded to perform analysis.")