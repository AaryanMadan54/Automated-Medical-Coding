import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class SentinelHybridAgent:
    def __init__(self, db, vector_engine):
        self.db = db
        self.ve = vector_engine
        self.llm_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # Using Llama 3.3 70B - fast, smart, and often free on Groq's dev tier
        self.model_name = "llama-3.3-70b-versatile"

    def analyze_note(self, note):
        # 1. Local Semantic Search
        candidates = self.ve.search_candidates(note, top_k=10)
        current_best = candidates[0]
        potential_upsell = candidates[1] if len(candidates) > 1 else None

        # 2. Generative Gap Analysis via Groq
        gap_report = self._generate_gap_fix(note, current_best, potential_upsell)
        
        # Log to Database
        self.db.log_encounter(
            note=note,
            code=current_best['code'],
            addendum=gap_report, # Saving the full report/addendum
            confidence=round(current_best['match_score'] * 100, 1)
        )

        return {
            "identified_code": current_best['code'],
            "confidence_score": round(current_best['match_score'] * 100, 1),
            "current_suggestion": current_best,
            "analysis": gap_report
        }

    def _generate_gap_fix(self, note, current, upsell):
        prompt = f"""
        You are a Medical Coding Auditor. Analyze this note:
        DOCTOR'S NOTE: "{note}"
        
        SELECTED CODE: {current['code']} ({current['description']})
        POTENTIAL UPSELL: {upsell['code']} ({upsell['description']})

        PROVIDE THREE THINGS:
        1. [AUDIT STATUS]: Is the current note sufficient for the Selected Code? (Pass/Fail)
        2. [ADDENDUM]: Write a 1-sentence addendum to prevent insurance denial for the Selected Code.
        3. [UPSELL OPPORTUNITY]: What specific clinical detail is missing to justify moving to the Potential Upsell code instead?
        """
        
        response = self.llm_client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content