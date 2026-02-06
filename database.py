import sqlite3
import json

class SentinelDB:
    def __init__(self, db_name="sentinel_core.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # CPT & Fees
        cursor.execute('''CREATE TABLE IF NOT EXISTS cpt_codes 
            (code TEXT PRIMARY KEY, description TEXT, category TEXT)''')
        
        # NCCI Edits (Bundling Rules: If col1 is billed, col2 is denied/bundled)
        cursor.execute('''CREATE TABLE IF NOT EXISTS ncci_edits 
            (col1 TEXT, col2 TEXT, modifier_allowed INTEGER)''')
        
        # Payer Specific Rules
        cursor.execute('''CREATE TABLE IF NOT EXISTS payer_rules 
            (payer_id TEXT, cpt_code TEXT, min_documentation_length INTEGER, req_vitals TEXT)''')
        
        # Audit Trails
        cursor.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            doctor_note TEXT,
            suggested_code TEXT,
            addendum TEXT,
            confidence REAL
        )''')
        
        self.conn.commit()

    def log_encounter(self, note, code, addendum, confidence):
        """Saves the AI's work to audit trails."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO audit_logs (doctor_note, suggested_code, addendum, confidence)
            VALUES (?, ?, ?, ?)
        ''', (note, code, addendum, confidence))
        self.conn.commit()
        print(f"Logged encounter to audit trails.")

    def import_cpt_json(self, json_data):
        """Pass your list of 1000+ CPT dicts here"""
        cursor = self.conn.cursor()
        data = [(i['code'], i['description'], i.get('category', 'General')) for i in json_data]
        cursor.executemany("INSERT OR REPLACE INTO cpt_codes VALUES (?, ?, ?)", data)
        self.conn.commit()
        print(f"Imported {len(json_data)} codes into SQL.")

    def get_bundling_rule(self, code1, code2):
        cursor = self.conn.cursor()
        cursor.execute("SELECT modifier_allowed FROM ncci_edits WHERE col1=? AND col2=?", (code1, code2))
        return cursor.fetchone()

# Initialize with some 2026 NCCI logic
db = SentinelDB()
# Mock NCCI: 99214 (Office Visit) bundles 93000 (EKG)
db.conn.execute("INSERT OR REPLACE INTO ncci_edits VALUES ('99214', '93000', 1)")
db.conn.commit()