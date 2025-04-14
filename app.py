
import streamlit as st
import pandas as pd

st.title("CT Cannabis Strain Analyzer")

@st.cache_data
def load_data():
    return pd.read_csv("final_strain_data_combined.csv")

df = load_data()

search_term = st.text_input("Enter strain name or keyword:")
if search_term:
    matches = df[df["strain"].str.contains(search_term.strip(), case=False, na=False)]
    if not matches.empty:
        st.write(f"Showing results for '{search_term}':")
        st.dataframe(matches)
        csv = matches.to_csv(index=False).encode("utf-8")
        st.download_button("Download Matching Strains", csv, "matched_strains.csv", "text/csv")
    else:
        st.warning("No matching strains found.")
else:
    st.info("Enter a search term to find matching strains.")
