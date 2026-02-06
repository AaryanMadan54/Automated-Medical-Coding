from datasets import load_dataset
import json
import os

def fetch_and_save_data():
    print("Downloading dataset 'atta00/cpt-hcpcs-codes'...")
    try:
        # Load dataset - using 'train' and 'test'
        ds = load_dataset("atta00/cpt-hcpcs-codes")
        
        combined_data = []
        
        # Iterate over available splits (usually train/test)
        for split in ds.keys():
            print(f"Processing split: {split}")
            for item in ds[split]:
                # We need to standardize the format for our app
                # Our app expects: {"code": "...", "description": "...", "category": "..."}
                
                # Let's check available keys in the first item of the first split
                if len(combined_data) == 0:
                    print(f"Sample item keys: {item.keys()}")
                
                # Mapping logic (update based on actual keys)
                # Fallback to probable keys if specific ones aren't found
                code = item.get('cpt_code') or item.get('code') or item.get('CPT_CODE')
                desc = item.get('long_description') or item.get('description') or item.get('LONG_DESCRIPTION')
                cat = item.get('category') or "General" # HF dataset might not have category, default to General
                
                if code and desc:
                    combined_data.append({
                        "code": str(code).strip(),
                        "description": str(desc).strip(),
                        "category": str(cat).strip()
                    })
        
        output_file = "cpt_hcpcs_codes.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=4)
            
        print(f"Successfully saved {len(combined_data)} codes to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
