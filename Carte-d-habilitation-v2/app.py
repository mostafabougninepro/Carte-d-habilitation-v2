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

# Section Modèle
selected_modele = st.selectbox("Choisissez le modèle de carte :", options_modeles)

# Extract default function name from model choice
modele_default_fonction = selected_modele.split("(")[-1].replace(")", "").strip()

# Section Recherche Matricule
matricule_search = st.text_input(
    "🔍 Rechercher par Matricule :", placeholder="Ex: 42685P"
)

agent_found = get_agent_data(matricule_search) if matricule_search else None

# Default values
default_nom = agent_found["Nom"] if agent_found else ""
default_prenom = agent_found["Prenom"] if agent_found else ""
default_mat = (
    agent_found["Matricule"] if agent_found else matricule_search or ""
)

# Fonction par défaut (De l'agent si trouvé, sinon du modèle sélectionné)
default_fonction = (
    agent_found["Fonction"]
    if (agent_found and agent_found["Fonction"])
    else modele_default_fonction
)

default_dt_auth = agent_found["Date_Autorisation"] if agent_found else ""
default_dt_med = agent_found["Examen_Medical"] if agent_found else ""
default_dt_psy = agent_found["Examen_Psychotechnique"] if agent_found else ""
default_dt_prof = agent_found["Examen_Professionnel"] if agent_found else ""
default_lignes = (
    agent_found["Ligne_Site"]
    if agent_found
    else "Kenitra - Casa / Lignes autorisées"
)
default_engins = (
    agent_found["Engin"]
    if agent_found
    else "E1450 , E1400 ,E1250 ,DH400,Z2M"
)

# Photo upload + Preview
uploaded_photo = st.file_uploader(
    "Photo d'identité (JPG / PNG)", type=["jpg", "jpeg", "png"]
)
if uploaded_photo is not None:
    st.image(uploaded_photo, caption="Aperçu de la photo", width=120)

st.markdown("---")

# Formulaire éditable des informations
st.subheader("Informations de l'Agent")

col1, col2 = st.columns(2)

with col1:
    nom_input = st.text_input("Nom", value=default_nom)
    matricule_input = st.text_input("Matricule", value=default_mat)
    fonction_input = st.text_input(
        "Fonction (Titre d'habilitation)", value=default_fonction
    )
    dt_autorisation = st.text_input(
        "Date d'autorisation", value=default_dt_auth
    )
    dt_medical = st.text_input("Date examen médical", value=default_dt_med)

with col2:
    prenom_input = st.text_input("Prénom", value=default_prenom)
    dt_professionnel = st.text_input(
        "Date examen professionnel", value=default_dt_prof
    )
    dt_psycho = st.text_input(
        "Date examen psychotechnique", value=default_dt_psy
    )

lignes_sites = st.text_input("Lignes / Sites autorisés", value=default_lignes)
materiel_locos = st.text_input(
    "Matériel / Locos / Rames", value=default_engins
)


# Génération du fichier Excel
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

    # Ecriture Fonction f cell D4
    sheet["D4"] = fonction_input

    # Remplissage des textes
    sheet["F5"] = nom_input
    sheet["J5"] = prenom_input
    sheet["F6"] = matricule_input
    sheet["F8"] = dt_autorisation
    sheet["F9"] = dt_professionnel
    sheet["F10"] = dt_medical
    sheet["F11"] = dt_psycho

    # Injection Matériel et Lignes
    sheet["L4"] = materiel_locos
    sheet["Q4"] = lignes_sites

    # Insertion de la photo
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
