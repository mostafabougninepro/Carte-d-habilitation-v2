import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Carte d'Habilitation - EPTC Kénitra",
    page_icon="🪪",
    layout="centered",
)

st.title("🪪 Système Génération Carte d'Habilitation")


# Function to retrieve agent data from Excel registry
@st.cache_data
def get_agent_data(matricule):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(
        base_dir, "Registre des habilitations EPTC KENITRA 2026.xlsx"
    )

    if not os.path.exists(excel_path):
        st.error(f"Fichier introuvable: {excel_path}")
        return None

    try:
        df = pd.read_excel(excel_path, sheet_name="Conduite", header=6)
        df["Matricule"] = df["Matricule"].astype(str).str.strip()
        agent = df[df["Matricule"] == str(matricule).strip()]

        if not agent.empty:
            data = agent.iloc[0]

            def fmt_date(val):
                if (
                    pd.notnull(val)
                    and str(val) != "NaT"
                    and str(val).strip() != ""
                ):
                    return pd.to_datetime(val).strftime("%Y-%m-%d")
                return ""

            nom_prenom = str(data.get("Nom /Prénom", "")).strip()

            return {
                "Matricule": str(data.get("Matricule", "")),
                "Nom_Prenom": nom_prenom,
                "Fonction": str(data.get("Fonction", "")).strip(),
                "Date_Autorisation": fmt_date(data.get("Date d'autorisation")),
                "Examen_Medical": fmt_date(data.get("Dernière  VM")),
                "Examen_Psychotechnique": fmt_date(data.get("Dernier Psy")),
                "Examen_Professionnel": fmt_date(data.get("Dernière évaluation")),
            }
    except Exception as e:
        st.error(f"Erreur de lecture du fichier: {e}")
    return None


# Determine template file based on agent function
def get_template_file(fonction):
    fonction_upper = fonction.upper()
    if "CONDUCTEUR DE LIGNE" in fonction_upper or "CL" in fonction_upper:
        return "CL.xlsx"
    elif "CHEF DE TRAIN" in fonction_upper or "CTR" in fonction_upper:
        return "CTR.xlsx"
    elif "CHEF FORMATION" in fonction_upper or "CFT" in fonction_upper:
        return "CFT.xlsx"
    elif "MANŒUVRE" in fonction_upper or "CRMV" in fonction_upper:
        return "CRMV.xlsx"
    return "CL.xlsx"


# UI Input
matricule_input = st.text_input(
    "🔍 Entrez le Matricule :", placeholder="Exemple: 42685P"
)

if matricule_input:
    agent = get_agent_data(matricule_input)

    if agent:
        template_file = get_template_file(agent["Fonction"])

        st.success(f"👤 **Nom & Prénom:** {agent['Nom_Prenom']}")
        st.info(
            f"💼 **Fonction:** {agent['Fonction']} | **Modèle:** `{template_file}`"
        )

        if agent["Date_Autorisation"]:
            st.markdown(
                f"📅 **Date d'autorisation:** `{agent['Date_Autorisation']}`"
            )

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="🩺 Examen Médical",
                value=agent["Examen_Medical"] or "—",
            )

        with col2:
            st.metric(
                label="🧠 Examen Psychotechnique",
                value=agent["Examen_Psychotechnique"] or "—",
            )

        with col3:
            st.metric(
                label="📝 Examen Professionnel",
                value=agent["Examen_Professionnel"] or "—",
            )

    else:
        st.error("❌ Matricule introuvable dans le registre.")
