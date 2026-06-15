import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI

st.set_page_config(page_title="Analiză Chestionar AI", page_icon="🤖", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("chestionar.xlsx")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

COL_MAP = {
    "1. Care este sexul dumneavoastra?": "Sex",
    "2. Care este varsta dumneavoastra?": "Vârstă",
    "3. Care este nivelul dumneavoastra de studii?": "Studii",
    "4. Care este domeniul dumneavoastra de activitate?": "Domeniu",
    "5. Care este statutul dumneavoastra profesional?": "Statut profesional",
    "7. Ati auzit pana acum de inteligenta artificiala?": "Auzit de AI",
    "8. Cat de familiarizat sunteti cu sistemele bazate pe inteligenta artificiala?": "Familiarizare AI (1-5)",
    "9. Ati utilizat pana acum platforme precum ChatGPT?": "Utilizat ChatGPT",
    "10. Cat de des utilizati sisteme AI?": "Frecvență utilizare AI",
    "11. In ce scop utilizati cel mai frecvent AI?": "Scop utilizare AI",
    "12. Considerati ca sistemele AI sunt usor de utilizat?": "Ușurință utilizare (1-5)",
    "13. Utilizati inteligenta artificiala in activitatea profesionala?": "AI la muncă",
    "14. Considerati ca AI contribuie la cresterea productivitatii la locul de munca?": "AI → Productivitate (1-5)",
    "15. Considerati ca AI reduce timpul necesar anumitor activitati?": "AI → Timp redus (1-5)",
    "16. Considerati ca AI este eficienta pentru automatizarea activitatilor repetitive?": "AI → Automatizare (1-5)",
    "17. Considerati ca abilitatea de a utiliza eficient AI va deveni importanta pe piata muncii?": "AI → Important pe piața muncii (1-5)",
    "18. Considerati ca AI poate imbunatati calitatea muncii?": "AI → Calitate muncă (1-5)",
    "19. Aveti incredere in raspunsurile generate de AI?": "Încredere în AI (1-5)",
    "20. Considerati ca informatiile generate de AI trebuie verificate de oameni?": "Verificare umană necesară",
    "21. Credeti ca AI poate genera informatii false sau eronate?": "AI poate genera erori",
    "22. Considerati ca utilizarea AI poate afecta confidentialitatea datelor?": "AI → Confidențialitate date",
    "23. Considerati ca utilizarea excesiva a AI poate reduce gandirea critica?": "AI → Gândire critică redusă (1-5)",
    "24. Credeti ca AI va reduce anumite locuri de munca?": "AI → Reducere locuri de muncă (1-5)",
    "25. Considerati ca anumite profesii sunt mai expuse automatizarii?": "Profesii expuse automatizării",
    "26. Va este teama ca AI ar putea influenta negativ siguranta locului dumneavoastra de munca?": "Teamă impact negativ job (1-5)",
    "27. Credeti ca AI va crea si noi locuri de munca?": "AI → Locuri noi de muncă",
    "28. Credeti ca AI va schimba semnificativ piata muncii in urmatorii 10 ani?": "AI → Schimbă piața muncii (1-5)",
    "29. Considerati ca inteligenta artificiala reprezinta:": "AI reprezintă",
    "30. Care considerati ca este principalul avantaj al utilizarii AI?": "Principal avantaj AI",
    "31. Care considerati ca este cel mai mare risc asociat dezvoltarii inteligentei artificiale?": "Principal risc AI",
    "32. Cum credeti ca va influenta AI viitorul profesional al oamenilor?": "AI → Viitor profesional",
}

SCALE_COLS = [k for k, v in COL_MAP.items() if "(1-5)" in v]

FILTER_COLS = [
    "1. Care este sexul dumneavoastra?",
    "2. Care este varsta dumneavoastra?",
    "3. Care este nivelul dumneavoastra de studii?",
    "4. Care este domeniul dumneavoastra de activitate?",
    "5. Care este statutul dumneavoastra profesional?",
    "10. Cat de des utilizati sisteme AI?",
    "11. In ce scop utilizati cel mai frecvent AI?",
    "29. Considerati ca inteligenta artificiala reprezinta:",
]

st.sidebar.title("🔍 Filtre")
st.sidebar.markdown("Selectează criteriile de filtrare:")

filtered_df = df.copy()
active_filters = {}

for col in FILTER_COLS:
    if col in df.columns:
        options = sorted(df[col].dropna().unique().tolist())
        if options:
            selected = st.sidebar.multiselect(COL_MAP.get(col, col), options=options, default=[])
            if selected:
                filtered_df = filtered_df[filtered_df[col].isin(selected)]
                active_filters[COL_MAP.get(col, col)] = selected

st.sidebar.markdown("---")
st.sidebar.metric("Respondenți selectați", len(filtered_df))
st.sidebar.metric("Total respondenți", len(df))

st.title("🤖 Analiză Chestionar — Percepția asupra Inteligenței Artificiale")
st.markdown(f"**{len(filtered_df)} din {len(df)} respondenți** corespund filtrelor aplicate.")

if active_filters:
    filter_text = " · ".join([f"**{k}**: {', '.join(str(v) for v in vals)}" for k, vals in active_filters.items()])
    st.info(f"Filtre active: {filter_text}")

if len(filtered_df) == 0:
    st.warning("Niciun respondent nu corespunde filtrelor selectate. Ajustează filtrele.")
    st.stop()

st.markdown("---")
st.header("👥 Profil Demografic")
col1, col2, col3 = st.columns(3)

with col1:
    sex_col = "1. Care este sexul dumneavoastra?"
    if sex_col in filtered_df.columns:
        sex_counts = filtered_df[sex_col].value_counts().reset_index()
        sex_counts.columns = ["Sex", "Număr"]
        fig = px.pie(sex_counts, names="Sex", values="Număr", title="Distribuție după sex",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

with col2:
    age_col = "2. Care este varsta dumneavoastra?"
    if age_col in filtered_df.columns:
        age_order = ["18-25 ani", "26-35 ani", "36-45 ani", "46-55 ani", "Peste 55 ani"]
        age_counts = filtered_df[age_col].value_counts().reindex(age_order).dropna().reset_index()
        age_counts.columns = ["Vârstă", "Număr"]
        fig = px.bar(age_counts, x="Vârstă", y="Număr", title="Distribuție după vârstă",
                     color="Număr", color_continuous_scale="Blues")
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

with col3:
    edu_col = "3. Care este nivelul dumneavoastra de studii?"
    if edu_col in filtered_df.columns:
        edu_counts = filtered_df[edu_col].value_counts().reset_index()
        edu_counts.columns = ["Studii", "Număr"]
        fig = px.pie(edu_counts, names="Studii", values="Număr", title="Distribuție după studii",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.header("💡 Familiarizare și Utilizare AI")
col1, col2 = st.columns(2)

with col1:
    freq_col = "10. Cat de des utilizati sisteme AI?"
    if freq_col in filtered_df.columns:
        freq_order = ["Zilnic", "De cateva ori pe saptamana", "Ocazional", "Niciodata"]
        freq_counts = filtered_df[freq_col].value_counts().reindex(freq_order).dropna().reset_index()
        freq_counts.columns = ["Frecvență", "Număr"]
        fig = px.bar(freq_counts, x="Frecvență", y="Număr", title="Cât de des utilizați AI?",
                     color="Număr", color_continuous_scale="Teal")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    scope_col = "11. In ce scop utilizati cel mai frecvent AI?"
    if scope_col in filtered_df.columns:
        scope_counts = filtered_df[scope_col].value_counts().reset_index()
        scope_counts.columns = ["Scop", "Număr"]
        fig = px.bar(scope_counts, x="Număr", y="Scop", orientation='h',
                     title="Scop principal de utilizare AI",
                     color="Număr", color_continuous_scale="Purples")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.header("💼 Percepție AI în Mediul Profesional")

work_scale_cols = [
    "14. Considerati ca AI contribuie la cresterea productivitatii la locul de munca?",
    "15. Considerati ca AI reduce timpul necesar anumitor activitati?",
    "16. Considerati ca AI este eficienta pentru automatizarea activitatilor repetitive?",
    "17. Considerati ca abilitatea de a utiliza eficient AI va deveni importanta pe piata muncii?",
    "18. Considerati ca AI poate imbunatati calitatea muncii?",
]
work_labels = ["Productivitate", "Timp redus", "Automatizare", "Important pe piața muncii", "Calitate muncă"]

means = []
for col in work_scale_cols:
    if col in filtered_df.columns:
        numeric = pd.to_numeric(filtered_df[col], errors='coerce')
        means.append(round(numeric.mean(), 2))
    else:
        means.append(0)

fig = go.Figure(go.Bar(
    x=means, y=work_labels, orientation='h',
    marker=dict(color=means, colorscale='RdYlGn', cmin=1, cmax=5,
                showscale=True, colorbar=dict(title="Medie")),
    text=[f"{m:.2f}" for m in means], textposition='outside'
))
fig.update_layout(title="Mediile scorurilor (scala 1-5) — AI și productivitatea la muncă",
                  xaxis=dict(range=[0, 5.5], title="Scor mediu"), height=350)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.header("⚠️ Riscuri și Încredere în AI")

risk_scale_cols = [
    "19. Aveti incredere in raspunsurile generate de AI?",
    "23. Considerati ca utilizarea excesiva a AI poate reduce gandirea critica?",
    "24. Credeti ca AI va reduce anumite locuri de munca?",
    "26. Va este teama ca AI ar putea influenta negativ siguranta locului dumneavoastra de munca?",
    "28. Credeti ca AI va schimba semnificativ piata muncii in urmatorii 10 ani?",
]
risk_labels = ["Încredere în AI", "AI reduce gândirea critică", "AI reduce locuri de muncă",
               "Teamă impact negativ job", "AI schimbă piața muncii"]

col1, col2 = st.columns([2, 1])

with col1:
    risk_means = []
    for col in risk_scale_cols:
        if col in filtered_df.columns:
            numeric = pd.to_numeric(filtered_df[col], errors='coerce')
            risk_means.append(round(numeric.mean(), 2))
        else:
            risk_means.append(0)

    fig = px.bar(x=risk_labels, y=risk_means,
                 title="Medii scoruri — Riscuri și Încredere (scala 1-5)",
                 color=risk_means, color_continuous_scale="RdYlBu",
                 text=[f"{m:.2f}" for m in risk_means])
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis=dict(range=[0, 5.5]), coloraxis_showscale=False,
                      xaxis_title="", yaxis_title="Scor mediu")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    perception_col = "29. Considerati ca inteligenta artificiala reprezinta:"
    if perception_col in filtered_df.columns:
        perc_counts = filtered_df[perception_col].value_counts().reset_index()
        perc_counts.columns = ["Percepție", "Număr"]
        fig = px.pie(perc_counts, names="Percepție", values="Număr", title="AI reprezintă...",
                     color_discrete_sequence=["#2ecc71", "#e74c3c", "#f39c12"])
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.header("🧠 Concluzii Generate de AI")
st.markdown("Apasă butonul pentru a genera automat o analiză a răspunsurilor selectate.")

def build_summary(dataframe):
    lines = [f"Număr respondenți analizați: {len(dataframe)}\n"]
    for col, label in [
        ("1. Care este sexul dumneavoastra?", "Sex"),
        ("2. Care este varsta dumneavoastra?", "Vârstă"),
        ("3. Care este nivelul dumneavoastra de studii?", "Studii"),
        ("4. Care este domeniul dumneavoastra de activitate?", "Domeniu"),
    ]:
        if col in dataframe.columns:
            counts = dataframe[col].value_counts()
            lines.append(f"{label}: {dict(counts)}")
    lines.append("\nScoruri medii (scala 1-5):")
    for col in SCALE_COLS:
        if col in dataframe.columns:
            val = pd.to_numeric(dataframe[col], errors='coerce').mean()
            if not pd.isna(val):
                lines.append(f"  - {COL_MAP.get(col, col)}: {val:.2f}/5")
    binary_cols = [
        "13. Utilizati inteligenta artificiala in activitatea profesionala?",
        "20. Considerati ca informatiile generate de AI trebuie verificate de oameni?",
        "21. Credeti ca AI poate genera informatii false sau eronate?",
        "25. Considerati ca anumite profesii sunt mai expuse automatizarii?",
        "27. Credeti ca AI va crea si noi locuri de munca?",
    ]
    lines.append("\nRăspunsuri Da/Nu:")
    for col in binary_cols:
        if col in dataframe.columns:
            counts = dataframe[col].value_counts()
            lines.append(f"  - {COL_MAP.get(col, col)}: {dict(counts)}")
    perc_col = "29. Considerati ca inteligenta artificiala reprezinta:"
    if perc_col in dataframe.columns:
        lines.append(f"\nPercepție AI: {dict(dataframe[perc_col].value_counts())}")
    return "\n".join(lines)

if st.button("✨ Generează concluzii cu AI", type="primary"):
    api_key = st.session_state.get("openai_api_key", "")
    if not api_key:
        st.error("Introdu cheia API OpenAI în câmpul de mai jos pentru a activa această funcție.")
    else:
        summary = build_summary(filtered_df)
        prompt = f"""Ești un analist de date specializat în studii sociale.
Analizează următoarele date dintr-un chestionar despre percepția inteligenței artificiale
și generează concluzii clare, structurate și relevante în limba română.

Date chestionar:
{summary}

Generează:
1. Un paragraf de sinteză generală (2-3 propoziții)
2. 3-4 concluzii principale, fiecare cu o explicație scurtă
3. O recomandare practică bazată pe date

Fii concis, obiectiv și bazează-te strict pe datele furnizate."""

        with st.spinner("Analizez datele cu AI..."):
            try:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=800
                )
                conclusion = response.choices[0].message.content
                st.success("Analiză completă!")
                st.markdown(conclusion)
            except Exception as e:
                st.error(f"Eroare la apelul API: {str(e)}")

with st.expander("⚙️ Configurare cheie API OpenAI"):
    key_input = st.text_input("Cheie API OpenAI", type="password",
                               value=st.session_state.get("openai_api_key", ""),
                               help="Obține cheia de la [platform.openai.com](https://platform.openai.com/api-keys)")
    if key_input:
        st.session_state["openai_api_key"] = key_input
        st.success("Cheie salvată în sesiune!")

st.markdown("---")
with st.expander("📋 Vezi datele brute filtrate"):
    display_df = filtered_df.copy()
    display_df.columns = [COL_MAP.get(c, c) for c in display_df.columns]
    st.dataframe(display_df, use_container_width=True)
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descarcă CSV filtrat", data=csv,
                       file_name="rezultate_filtrate.csv", mime="text/csv")
