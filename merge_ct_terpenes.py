
import pandas as pd
import re
import os

# ---- CONFIG ----
CT_DATA_URL = "https://data.ct.gov/resource/egd5-wb6r.csv"
EXISTING_DB_PATH = "existing_strain_data.csv"  # Replace with your actual path
OUTPUT_PATH = "merged_strain_data_with_ct.csv"

# ---- FUNCTIONS ----

def normalize_strain_name(name):
    return re.sub(r'[^\w\s]', '', str(name)).lower().strip()

def fetch_ct_data():
    df = pd.read_csv(CT_DATA_URL)
    df['normalized_strain'] = df['strain'].apply(normalize_strain_name)
    terpene_aliases = {
        'β-Caryophyllene': 'Caryophyllene',
        'α-Pinene': 'Pinene',
        'β-Myrcene': 'Myrcene',
        'd-Limonene': 'Limonene',
        'trans-Nerolidol': 'Nerolidol',
        'cis-Nerolidol': 'Nerolidol',
        'α-Humulene': 'Humulene',
        'Guaiol': 'Guaiol',
        'Linalool': 'Linalool',
        'Terpinolene': 'Terpinolene'
    }
    df['terpene_clean'] = df['terpene'].map(terpene_aliases).fillna(df['terpene'])
    return df

def load_existing_data(path):
    df = pd.read_csv(path)
    df['normalized_strain'] = df['strain'].apply(normalize_strain_name)
    df['terpenes'] = df['terpenes'].apply(eval) if isinstance(df['terpenes'].iloc[0], str) else df['terpenes']
    return df

def merge_data(existing_df, ct_df):
    for i, row in existing_df.iterrows():
        match_strain = row['normalized_strain']
        ct_matches = ct_df[ct_df['normalized_strain'] == match_strain]
        if not ct_matches.empty:
            existing_df.at[i, 'verified_in_CT'] = True
            existing_df.at[i, 'trust_score'] += 10
            ct_terpenes = set(ct_matches['terpene_clean'].unique())
            existing_terpenes = set(row['terpenes'])
            merged_terpenes = list(existing_terpenes.union(ct_terpenes))
            existing_df.at[i, 'terpenes'] = merged_terpenes
    return existing_df.drop(columns=['normalized_strain'])

def main():
    print("Fetching CT terpene data...")
    ct_df = fetch_ct_data()

    print("Loading existing strain data...")
    existing_df = load_existing_data(EXISTING_DB_PATH)

    print("Merging datasets...")
    merged_df = merge_data(existing_df, ct_df)

    print(f"Saving merged data to {OUTPUT_PATH}")
    merged_df.to_csv(OUTPUT_PATH, index=False)
    print("Merge complete.")

if __name__ == "__main__":
    main()
