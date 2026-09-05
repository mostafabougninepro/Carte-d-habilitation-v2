import io
import os
import openpyxl
from openpyxl.drawing.image import Image as OpenpyxlImage
import pandas as pd
from PIL import Image as PILImage
import streamlit as st

st.set_page_config(
    page_title="Générateur de Cartes d'Habilitation",
    page_icon="🪪",
    layout="centered",
)

st.title("🎴 Générateur de Cartes d'Habilitation")


# 1. Recherche des données dans le Registre Excel
@st.cache_data
def get_agent_data(matricule):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(
        base_dir, "Registre des habilitations EPTC KENITRA 2026.xlsx"
    )

    if not os.path.exists(excel_path):
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
                "Fonction": str(data.get("Fonction", "")).strip(),
                "Date_Autorisation": fmt_date(data.get("Date d'autorisation")),
                "Examen_Medical": fmt_date(data.get("Dernière  VM")),
                "Examen_Psychotechnique": fmt_date(data.get("Dernier Psy")),
                "Examen_Professionnel": fmt_date(data.get("Dernière évaluation")),
                "Engin": str(data.get("Engin ", ""))
                if pd.notnull(data.get("Engin "))
                else "",
                "Ligne_Site": str(data.get("Ligne / Site ", ""))
                if pd.notnull(data.get("Ligne / Site "))
                else "",
            }
    except Exception:
        pass
    return None


options_modeles = [
    "CTR (Chef de Train)",
    "CL (Conducteur de Ligne)",
    "CFT (Chef Formation Trains)",
    "CRMV (Conducteur de Manœuvre)",
]

# Modèle sélectionné
selected_modele = st.selectbox("Choisissez le modèle de carte :", options_modeles)
modele_default_fonction = selected_modele.split("(")[-1].replace(")", "").strip()

# Callback pour mettre à jour la fonction et les champs quand le matricule change
if "last_matricule" not in st.session_state:
    st.session_state["last_matricule"] = ""

matricule_search = st.text_input(
    "🔍 Rechercher par Matricule :", placeholder="Ex: 42685P"
)

# Chargement de l'agent
agent_found = get_agent_data(matricule_search) if matricule_search else None

# Si le matricule a changé ou un agent est trouvé, on réinitialise les champs
if matricule_search != st.session_state["last_matricule"]:
    st.session_state["last_matricule"] = matricule_search
    if agent_found:
        st.session_state["nom"] = agent_found["Nom"]
        st.session_state["prenom"] = agent_found["Prenom"]
        st.session_state["matricule"] = agent_found["Matricule"]
        st.session_state["fonction"] = (
            agent_found["Fonction"] if agent_found["Fonction"] else modele_default_fonction
        )
        st.session_state["dt_auth"] = agent_found["Date_Autorisation"]
        st.session_state["dt_med"] = agent_found["Examen_Medical"]
        st.session_state["dt_psy"] = agent_found["Examen_Psychotechnique"]
        st.session_state["dt_prof"] = agent_found["Examen_Professionnel"]
        st.session_state["lignes"] = (
            agent_found["Ligne_Site"] if agent_found["Ligne_Site"] else "Kenitra - Casa"
        )
        st.session_state["engins"] = (
            agent_found["Engin"] if agent_found["Engin"] else "E1450, E1400, Z2M"
        )
    else:
        st.session_state["fonction"] = modele_default_fonction

# Set initial defaults if not existing
st.session_state.setdefault("nom", "")
st.session_state.setdefault("prenom", "")
st.session_state.setdefault("matricule", matricule_search or "")
st.session_state.setdefault("fonction", modele_default_fonction)
st.session_state.setdefault("dt_auth", "")
st.session_state.setdefault("dt_med", "")
st.session_state.setdefault("dt_psy", "")
st.session_state.setdefault("dt_prof", "")
st.session_state.setdefault("lignes", "Kenitra - Casa")
st.session_state.setdefault("engins", "E1450, E1400, Z2M")

# Upload Photo
uploaded_photo = st.file_uploader(
    "Photo d'identité (JPG / PNG)", type=["jpg", "jpeg", "png"]
)
if uploaded_photo is not None:
    st.image(uploaded_photo, caption="Aperçu de la photo", width=120)

st.markdown("---")

# Formulaire
st.subheader("Informations de l'Agent")

col1, col2 = st.columns(2)

with col1:
    nom_input = st.text_input("Nom", key="nom")
    matricule_input = st.text_input("Matricule", key="matricule")
    fonction_input = st.text_input("Fonction (Titre d'habilitation)", key="fonction")
    dt_autorisation = st.text_input("Date d'autorisation", key="dt_auth")
    dt_medical = st.text_input("Date examen médical", key="dt_med")

with col2:
    prenom_input = st.text_input("Prénom", key="prenom")
    dt_professionnel = st.text_input("Date examen professionnel", key="dt_prof")
    dt_psycho = st.text_input("Date examen psychotechnique", key="dt_psy")

lignes_sites = st.text_input("Lignes / Sites autorisés", key="lignes")
materiel_locos = st.text_input("Matériel / Locos / Rames", key="engins")


# Génération Excel
def generate_custom_excel():
    template_map = {
        "CTR (Chef de Train)": "CTR.xlsx",
        "CL (Conducteur de Ligne)": "CL.xlsx",
        "CFT (Chef Formation Trains)": "CFT.xlsx",
        "CRMV (Conducteur de Manœuvre)": "CRMV.xlsx",
    }
    tmpl = template_map.get(selected_modele, "CL.xlsx")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tmpl_path = os.path.join(base_dir, tmpl)

    wb = openpyxl.load_workbook(tmpl_path)
    sheet = wb.active

    sheet["D4"] = fonction_input
    sheet["F5"] = nom_input
    sheet["J5"] = prenom_input
    sheet["F6"] = matricule_input
    sheet["F8"] = dt_autorisation
    sheet["F9"] = dt_professionnel
    sheet["F10"] = dt_medical
    sheet["F11"] = dt_psycho

    sheet["L4"] = materiel_locos
    sheet["Q4"] = lignes_sites

    if uploaded_photo is not None:
        img_bytes = uploaded_photo.read()
        pil_img = PILImage.open(io.BytesIO(img_bytes))
        pil_img = pil_img.resize((100, 120))

        img_temp_path = os.path.join(base_dir, "_temp_photo.png")
        pil_img.save(img_temp_path)

        xl_img = OpenpyxlImage(img_temp_path)
        sheet.add_image(xl_img, "B5")

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


st.write("")
if st.button("⚡ Générer la Carte"):
    excel_file = generate_custom_excel()
    st.success("✅ Carte générée avec succès !")
    st.download_button(
        label="📥 Télécharger la Carte (Excel)",
        data=excel_file,
        file_name=f"Carte_{matricule_input or 'Agent'}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
