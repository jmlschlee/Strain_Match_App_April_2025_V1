
import streamlit as st
import pandas as pd
import difflib

st.title("CT Cannabis Strain Analyzer with Terpene Unification")

@st.cache_data
def load_data():
    return pd.read_csv("final_strain_data_combined.csv")

def unify_terpenes(df):
    terpene_cols = [col for col in df.columns if col.upper() == col and col not in ['THC', 'CBD']]
    unified = {}
    for terp in terpene_cols:
        match_found = False
        for key in unified:
            if any(seq in terp.lower() for seq in key.lower().split()) or difflib.SequenceMatcher(None, key.lower(), terp.lower()).ratio() > 0.7:
                unified[key].append(terp)
                match_found = True
                break
        if not match_found:
            unified[terp] = [terp]

    for unified_name, variants in unified.items():
        if len(variants) > 1:
            df[unified_name + "_unified"] = df[variants].sum(axis=1)
        else:
            df[unified_name + "_unified"] = df[variants[0]]

    return df, list(unified.keys())

df = load_data()
df, unified_terpenes = unify_terpenes(df)

search_term = st.text_input("Enter strain name or keyword:")
if search_term:
    matches = df[df["strain"].str.contains(search_term.strip(), case=False, na=False)]
    if not matches.empty:
        st.write(f"Showing results for '{search_term}':")
        st.dataframe(matches[["strain", "terpenes", "trust_score", "verified_in_CT"] + [t + "_unified" for t in unified_terpenes]])
        csv = matches.to_csv(index=False).encode("utf-8")
        st.download_button("Download Matching Strains", csv, "matched_strains.csv", "text/csv")
    else:
        st.warning("No matching strains found.")
else:
    st.info("Enter a search term to find matching strains.")
