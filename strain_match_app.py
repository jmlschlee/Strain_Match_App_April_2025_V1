
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
import io

st.set_page_config(page_title="Cannabis Strain Matchmaker", layout="wide")

st.title("🌿 Cannabis Strain Matchmaker")
st.markdown("Input up to 5 conditions and receive a ranked list of cannabis strains based on terpene alignment and research-backed benefits.")

st.sidebar.header("🔍 Filter Preferences")
thc_free = st.sidebar.checkbox("Exclude High-THC Strains")
calming = st.sidebar.checkbox("Prefer Calming Effects")
energizing = st.sidebar.checkbox("Prefer Energizing Effects")
exclude_terpenes = st.sidebar.text_input("Exclude Terpenes (comma-separated)")
excluded_terpene_set = set(map(str.strip, exclude_terpenes.split(","))) if exclude_terpenes else set()

st.subheader("📝 Enter up to 5 conditions")
conditions = []
for i in range(1, 6):
    cond = st.text_input(f"Condition {i}", "" if i > 1 else "Anxiety")
    if cond:
        conditions.append(cond.strip())

condition_data = pd.read_csv("/mnt/data/Expanded_Condition-Terpene_Mapping_with_Confidence_Levels.csv")
condition_data["Helpful_Terpenes"] = condition_data["Helpful_Terpenes"].apply(eval)
condition_data["Avoid_Terpenes"] = condition_data["Avoid_Terpenes"].apply(eval)
mental_health_data = pd.read_csv("/mnt/data/Mental_Health_Conditions_and_Terpene_Effects.csv")

strain_data = pd.DataFrame({
    "Strain": [
        "Granddaddy Purple", "Northern Lights", "Harlequin", "Cannatonic", "ACDC",
        "Sour Diesel", "Blue Dream", "Jack Herer", "Girl Scout Cookies", "Pineapple Express",
        "Green Crack", "Bubba Kush", "Tangie", "Cherry Pie", "White Widow"
    ],
    "Dominant_Terpenes": [
        ["Myrcene", "Linalool", "Caryophyllene"], ["Myrcene", "Linalool", "Caryophyllene"], ["Caryophyllene", "Myrcene", "CBD"],
        ["Caryophyllene", "Linalool", "CBD"], ["CBD", "Caryophyllene", "Pinene"], ["Limonene", "Caryophyllene", "THC"],
        ["Limonene", "Pinene", "Myrcene"], ["Pinene", "Terpinolene", "Limonene"], ["Caryophyllene", "Limonene", "Myrcene"],
        ["Limonene", "Myrcene", "Pinene"], ["Limonene", "Pinene", "THC"], ["Myrcene", "Caryophyllene", "Linalool"],
        ["Limonene", "Terpinolene", "Pinene"], ["Myrcene", "Linalool", "Caryophyllene"], ["Pinene", "Myrcene", "Caryophyllene"]
    ]
})

def match_strains(conditions, cond_df, strain_df):
    helpful_set = set()
    avoid_set = set()
    confidence_info = {}
    for _, row in cond_df[cond_df['Condition'].isin(conditions)].iterrows():
        helpful_set.update(row['Helpful_Terpenes'])
        avoid_set.update(row['Avoid_Terpenes'])
        confidence_info[row['Condition']] = row.get('Confidence_Level', 'Unknown')

    results = []
    for _, row in strain_df.iterrows():
        name = row['Strain']
        terpenes = set(row['Dominant_Terpenes'])
        if thc_free and "THC" in terpenes:
            continue
        if excluded_terpene_set and terpenes & excluded_terpene_set:
            continue
        helpful_match = len(terpenes & helpful_set)
        harmful_match = len(terpenes & avoid_set)
        score = max(0, helpful_match * 10 - harmful_match * 15)
        results.append({
            "Strain": name,
            "Helpful Terpenes": list(terpenes & helpful_set),
            "Conflicting Terpenes": list(terpenes & avoid_set),
            "Match Score": score
        })

    sorted_results = sorted(results, key=lambda x: x["Match Score"], reverse=True)
    top = sorted_results[:10]
    caution = [r for r in sorted_results[10:] if r["Match Score"] <= 5]
    return top, caution, confidence_info

def export_pdf(results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Cannabis Strain Matchmaker Results", ln=True, align='C')
    for r in results:
        pdf.cell(200, 10, txt=f"{r['Strain']} — {r['Match Score']}%", ln=True)
    return pdf.output(dest='S').encode("latin1")

if st.button("Match My Strains") and conditions:
    top_matches, caution_strains, confidence_info = match_strains(conditions, condition_data, strain_data)

    st.subheader("🌱 Top Matches")
    for match in top_matches:
        st.markdown(f"**{match['Strain']}** — {match['Match Score']}% match")
        st.markdown(f"Helpful: {', '.join(match['Helpful Terpenes'])}")
        st.markdown(f"Conflicts: {', '.join(match['Conflicting Terpenes']) or 'None'}")
        st.progress(match['Match Score'] / 100)
        st.markdown("---")

    if caution_strains:
        st.subheader("⚠️ Caution Strains")
        for strain in caution_strains:
            st.markdown(f"**{strain['Strain']}** — {strain['Match Score']}% match (Potential terpene conflicts)")
            st.markdown(f"Conflicting Terpenes: {', '.join(strain['Conflicting Terpenes'])}")
            st.markdown("---")

    st.subheader("📚 Confidence Levels")
    for cond in conditions:
        level = confidence_info.get(cond, "Unknown")
        st.markdown(f"- {cond}: {level} confidence")

    scores = [x['Match Score'] for x in top_matches]
    names = [x['Strain'] for x in top_matches]
    fig, ax = plt.subplots()
    ax.barh(names, scores)
    ax.set_xlabel("Match Score")
    ax.set_title("Top Strain Matches")
    st.pyplot(fig)

    if st.button("📤 Export to PDF"):
        pdf_data = export_pdf(top_matches)
        b64 = base64.b64encode(pdf_data).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="strain_matches.pdf">Download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

    email = st.text_input("✉️ Enter email to send results (simulated):")
    if st.button("Send Results") and email:
        st.success(f"Simulated sending to {email}. (Feature requires backend integration)")

elif not conditions:
    st.warning("Please enter at least one condition to get started.")
