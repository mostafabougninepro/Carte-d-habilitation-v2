import io
import os
import openpyxl
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Carte d'Habilitation - EPTC Kénitra",
    page_icon="🪪",
    layout="centered",
)

st.title("🪪 Système Génération Carte d'Habilitation")


# 1. Extraction des données depuis le Registre
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
            parts = nom_prenom.split(" ", 1)

            return {
                "Matricule": str(data.get("Matricule", "")),
                "Nom": parts[0] if len(parts) > 0 else "",
                "Prenom": parts[1] if len(parts) > 1 else "",
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


# 2. Détermination du modèle
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


# 3. Remplissage du modèle Excel
def generate_excel_card(agent, template_filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, template_filename)

    wb = openpyxl.load_workbook(template_path)
    sheet = wb.active

    # Insertion des données dans les cellules du modèle
    sheet["F5"] = agent["Nom"]
    sheet["J5"] = agent["Prenom"]
    sheet["F6"] = agent["Matricule"]
    sheet["F8"] = agent["Date_Autorisation"]
    sheet["F9"] = agent["Examen_Professionnel"]
    sheet["F10"] = agent["Examen_Medical"]
    sheet["F11"] = agent["Examen_Psychotechnique"]

    # Sauvegarde en mémoire
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# Interface Utilisateur
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

        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🩺 Examen Médical", agent["Examen_Medical"] or "—")
        with col2:
            st.metric(
                "🧠 Examen Psychotechnique",
                agent["Examen_Psychotechnique"] or "—",
            )
        with col3:
            st.metric(
                "📝 Examen Professionnel",
                agent["Examen_Professionnel"] or "—",
            )

        st.divider()

        # Génération du fichier Excel à télécharger
        excel_data = generate_excel_card(agent, template_file)

        # Bouton de Téléchargement
        st.download_button(
            label="📥 Télécharger la Carte d'Habilitation (Excel)",
            data=excel_data,
            file_name=f"Carte_Habilitation_{agent['Matricule']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    else:
        st.error("❌ Matricule introuvable dans le registre.")
