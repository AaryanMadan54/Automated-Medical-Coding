from sentence_transformers import SentenceTransformer, util
import numpy as np

class SentinelVectorEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.code_embeddings = None
        self.metadata = []

    def index_codes(self, cpt_list):
        """Indexes CPT codes for semantic search"""
        descriptions = [item['description'] for item in cpt_list]
        self.metadata = cpt_list
        self.code_embeddings = self.model.encode(descriptions, convert_to_tensor=True)
        print(f"Indexed {len(cpt_list)} codes for Semantic RAG.")

    def search_candidates(self, note, top_k):
        note_vec = self.model.encode(note, convert_to_tensor=True)
        hits = util.semantic_search(note_vec, self.code_embeddings, top_k=top_k)
        return [self.metadata[hit['corpus_id']] | {'match_score': hit['score']} for hit in hits[0]]