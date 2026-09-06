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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_agent_photo(matricule):
    if not matricule or not str(matricule).strip():
        return None, "Matricule vide"

    target = str(matricule).strip().lower()

    valid_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".JPG",
        ".JPEG",
        ".PNG",
        ".Jpg",
    ]

    possible_folders = [
        os.path.join(BASE_DIR, "photo A"),
        os.path.join(BASE_DIR, "photo B"),
        os.path.join(BASE_DIR, "Carte-d-habilitation-v2", "photo A"),
        os.path.join(BASE_DIR, "Carte-d-habilitation-v2", "photo B"),
        os.path.join(os.getcwd(), "photo A"),
        os.path.join(os.getcwd(), "photo B"),
        os.path.join(os.getcwd(), "Carte-d-habilitation-v2", "photo A"),
        os.path.join(os.getcwd(), "Carte-d-habilitation-v2", "photo B"),
    ]

    for folder_path in possible_folders:
        if os.path.exists(folder_path):
            try:
                for file_name in os.listdir(folder_path):
                    name_part, ext = os.path.splitext(file_name)
                    if (
                        name_part.strip().lower() == target
                        and ext in valid_extensions
                    ):
                        full_path = os.path.join(folder_path, file_name)
                        folder_name = os.path.basename(folder_path)
                        return (
                            full_path,
                            f"Photo trouvée dans [{folder_name}]",
                        )
            except Exception:
                continue

    for root, dirs, files in os.walk(BASE_DIR):
        for file_name in files:
            name_part, ext = os.path.splitext(file_name)
            if (
                name_part.strip().lower() == target
                and ext.lower() in valid_extensions
            ):
                full_path = os.path.join(root, file_name)
                folder_name = os.path.basename(root)
                return full_path, f"Photo trouvée dans [{folder_name}]"

    return None, "Non trouvée dans les dossiers"


def get_agent_data(matricule):
    excel_filename = None
    for f in os.listdir(BASE_DIR):
        if f.lower().endswith(".xlsx") and "registre" in f.lower():
            excel_filename = f
            break

    if not excel_filename:
        st.error("⚠️ Fichier Excel du registre introuvable !")
        return None

    excel_path = os.path.join(BASE_DIR, excel_filename)

    try:
        xl = pd.ExcelFile(excel_path)

        for sheet_name in xl.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name, header=6)
            df.columns = [str(c).strip() for c in df.columns]

            if "Matricule" in df.columns:
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

                    nom_val = ""
                    prenom_val = ""

                    if "Nom" in data and pd.notnull(data["Nom"]):
                        nom_val = str(data["Nom"]).strip()
                    if "Prénom" in data and pd.notnull(data["Prénom"]):
                        prenom_val = str(data["Prénom"]).strip()

                    if not nom_val and not prenom_val:
                        for col in df.columns:
                            if "nom" in col.lower():
                                val = str(data.get(col, "")).strip()
                                if val and val.lower() != "nan":
                                    parts = val.split(" ", 1)
                                    nom_val = parts[0] if len(parts) > 0 else ""
                                    prenom_val = (
                                        parts[1] if len(parts) > 1 else ""
                                    )
                                    break

                    fonction_val = str(data.get("Fonction", "")).strip()
                    if fonction_val.lower() == "nan":
                        fonction_val = ""

                    ligne_site_val = ""
                    for col in df.columns:
                        if "ligne" in col.lower() or "site" in col.lower():
                            val = data.get(col, "")
                            if pd.notnull(val) and str(val).lower() != "nan":
                                ligne_site_val = str(val).strip()
                                break

                    engin_val = ""
                    for col in df.columns:
                        if "engin" in col.lower() or "materiel" in col.lower():
                            val = data.get(col, "")
                            if pd.notnull(val) and str(val).lower() != "nan":
                                engin_val = str(val).strip()
                                break

                    return {
                        "Matricule": str(data.get("Matricule", "")),
                        "Nom": nom_val,
                        "Prenom": prenom_val,
                        "Fonction": fonction_val,
                        "Date_Autorisation": fmt_date(
                            data.get("Date d'autorisation")
                        ),
                        "Examen_Medical": fmt_date(
                            data.get(
                                "Dernière  VM", data.get("Dernière VM", "")
                            )
                        ),
                        "Examen_Psychotechnique": fmt_date(
                            data.get(
                                "Dernier Psy", data.get("Dernière Psy", "")
                            )
                        ),
                        "Examen_Professionnel": fmt_date(
                            data.get(
                                "Dernière évaluation",
                                data.get("Dernier Eval", ""),
                            )
                        ),
                        "Engin": engin_val,
                        "Ligne_Site": ligne_site_val,
                    }
    except Exception as e:
        st.error(f"Erreur de lecture du registre : {e}")
    return None


options_modeles = [
    "CTR (Chef de Train)",
    "CL (Conducteur de Ligne)",
    "CFT (Chef Formation Trains)",
    "CRMV (Conducteur de Manœuvre)",
]

selected_modele = st.selectbox("Choisissez le modèle de carte :", options_modeles)
modele_default_fonction = selected_modele.split("(")[-1].replace(")", "").strip()

if "CRMV" in selected_modele:
    default_engins = "E1450, E1400, Z2M, DH400, DM600"
    default_site = "Site Voyageurs Kénitra"
elif "CFT" in selected_modele:
    default_engins = "E1450, E1400, E1250, Z2M, DH400, DM600"
    default_site = "Site Voyageurs Kénitra"
elif "CTR" in selected_modele:
    default_engins = "E1450, E1400, E1250, Z2M, DH400"
    default_site = ""
elif "CL" in selected_modele:
    default_engins = "E1450, E1400, Z2M"
    default_site = ""
else:
    default_engins = ""
    default_site = ""

if "last_matricule" not in st.session_state:
    st.session_state["last_matricule"] = ""

matricule_search = st.text_input(
    "🔍 Rechercher par Matricule :", placeholder="Ex: 47622S"
)

agent_found = get_agent_data(matricule_search) if matricule_search else None

if matricule_search != st.session_state["last_matricule"]:
    st.session_state["last_matricule"] = matricule_search
    if agent_found:
        st.session_state["nom"] = agent_found["Nom"]
        st.session_state["prenom"] = agent_found["Prenom"]
        st.session_state["matricule"] = agent_found["Matricule"]
        st.session_state["fonction"] = (
            agent_found["Fonction"]
            if agent_found["Fonction"]
            else modele_default_fonction
        )
        st.session_state["dt_auth"] = agent_found["Date_Autorisation"]
        st.session_state["dt_med"] = agent_found["Examen_Medical"]
        st.session_state["dt_psy"] = agent_found["Examen_Psychotechnique"]
        st.session_state["dt_prof"] = agent_found["Examen_Professionnel"]

        if "CFT" in selected_modele or "CRMV" in selected_modele:
            st.session_state["lignes"] = "Site Voyageurs Kénitra"
        else:
            st.session_state["lignes"] = (
                agent_found["Ligne_Site"]
                if agent_found["Ligne_Site"]
                else default_site
            )

        st.session_state["engins"] = (
            agent_found["Engin"] if agent_found["Engin"] else default_engins
        )
    else:
        st.session_state["fonction"] = modele_default_fonction
        st.session_state["engins"] = default_engins
        st.session_state["lignes"] = default_site

st.session_state.setdefault("nom", "")
st.session_state.setdefault("prenom", "")
st.session_state.setdefault("matricule", matricule_search or "")
st.session_state.setdefault("fonction", modele_default_fonction)
st.session_state.setdefault("dt_auth", "")
st.session_state.setdefault("dt_med", "")
st.session_state.setdefault("dt_psy", "")
st.session_state.setdefault("dt_prof", "")
st.session_state.setdefault("lignes", default_site)
st.session_state.setdefault("engins", default_engins)

found_photo_path, search_status = get_agent_photo(matricule_search)

uploaded_photo = st.file_uploader(
    "Photo d'identité (JPG / PNG)", type=["jpg", "jpeg", "png"]
)

final_photo_source = None

if uploaded_photo is not None:
    final_photo_source = uploaded_photo
    st.image(uploaded_photo, caption="Photo importée manuellement", width=120)
elif found_photo_path:
    final_photo_source = found_photo_path
    st.image(found_photo_path, caption=f"✅ {search_status}", width=120)
elif matricule_search.strip():
    st.warning(f"⚠️ {search_status} ({matricule_search})")

st.markdown("---")
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


def generate_custom_excel():
    template_map = {
        "CTR (Chef de Train)": "CTR.xlsx",
        "CL (Conducteur de Ligne)": "CL.xlsx",
        "CFT (Chef Formation Trains)": "CFT.xlsx",
        "CRMV (Conducteur de Manœuvre)": "CRMV.xlsx",
    }
    target_tmpl = template_map.get(selected_modele, "CFT.xlsx")

    tmpl_path = None
    for f in os.listdir(BASE_DIR):
        if f.lower() == target_tmpl.lower():
            tmpl_path = os.path.join(BASE_DIR, f)
            break

    if not tmpl_path:
        tmpl_path = os.path.join(BASE_DIR, target_tmpl)

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

    if final_photo_source is not None:
        if isinstance(final_photo_source, str):
            pil_img = PILImage.open(final_photo_source)
        else:
            img_bytes = final_photo_source.read()
            pil_img = PILImage.open(io.BytesIO(img_bytes))

        pil_img = pil_img.resize((100, 120))

        img_temp_path = os.path.join(BASE_DIR, "_temp_photo.png")
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

    modele_code = selected_modele.split("(")[0].strip()
    clean_nom = nom_input.strip() if nom_input.strip() else "Agent"
    custom_filename = f"Carte_{modele_code}_{clean_nom}.xlsx"

    st.success("✅ Carte générée avec succès !")
    st.download_button(
        label="📥 Télécharger la Carte (Excel)",
        data=excel_file,
        file_name=custom_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
