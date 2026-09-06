import io
import os
import openpyxl
from openpyxl.drawing.image import Image as OpenpyxlImage
import pandas as pd
from PIL import Image as PILImage
import streamlit as st

st.set_page_config(
    page_title="Système Management Sécurité",
    page_icon="🛡️",
    layout="centered",
)

st.title("🛡️ Système Management Sécurité")
st.subheader("Générateur de Cartes d'Habilitation")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_agent_photo(matricule):
    if not matricule or not str(matricule).strip():
        return None, "Matricule vide"

    target = str(matricule).strip().lower()
    folders = ["photo A", "photo B", "photoA", "photoB"]

    for folder in folders:
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.exists(folder_path):
            try:
                for file_name in os.listdir(folder_path):
                    name_part, ext = os.path.splitext(file_name)
                    if name_part.strip().lower() == target:
                        full_path = os.path.join(folder_path, file_name)
                        return full_path, f"Photo trouvée dans [{folder}]"
            except Exception:
                continue

    return None, "Photo non trouvable"


def get_official_agent_info(matricule):
    """قراءة الاسم والكنية والوظيفة من ملف التحديث Mis_A_Jour photos.xlsx"""
    excel_path = os.path.join(BASE_DIR, "Mis_A_Jour photos.xlsx")
    if not os.path.exists(excel_path):
        return None

    try:
        xl = pd.ExcelFile(excel_path)
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # البحث عن الأعمدة المناسبة
            mle_col = None
            for col in df.columns:
                if str(col).strip().lower() in ["mle", "matricule"]:
                    mle_col = col
                    break
            
            if mle_col:
                df[mle_col] = df[mle_col].astype(str).str.strip()
                agent = df[df[mle_col].str.lower() == str(matricule).strip().lower()]
                
                if not agent.empty:
                    row = agent.iloc[0]
                    nom = str(row.get("Nom", "")).strip() if pd.notnull(row.get("Nom")) else ""
                    prenom = str(row.get("Prénom", "")).strip() if pd.notnull(row.get("Prénom")) else ""
                    fonction = str(row.get("Fonction", "")).strip() if pd.notnull(row.get("Fonction")) else ""
                    return {"Nom": nom, "Prenom": prenom, "Fonction": fonction}
    except Exception:
        pass
    return None


def get_agent_dates_and_details(matricule):
    """قراءة التواريخ والـ Engin والـ Site من الـ Registre"""
    excel_filename = None
    for f in os.listdir(BASE_DIR):
        if f.lower().endswith(".xlsx") and "registre" in f.lower():
            excel_filename = f
            break

    if not excel_filename:
        return {}

    excel_path = os.path.join(BASE_DIR, excel_filename)

    try:
        xl = pd.ExcelFile(excel_path)
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name, header=6)
            df.columns = [str(c).strip() for c in df.columns]

            if "Matricule" in df.columns:
                df["Matricule"] = df["Matricule"].astype(str).str.strip()
                agent = df[df["Matricule"].str.lower() == str(matricule).strip().lower()]

                if not agent.empty:
                    data = agent.iloc[0]

                    def fmt_date(val):
                        if pd.notnull(val) and str(val) != "NaT" and str(val).strip() != "":
                            return pd.to_datetime(val).strftime("%Y-%m-%d")
                        return ""

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
                        "Date_Autorisation": fmt_date(data.get("Date d'autorisation")),
                        "Examen_Medical": fmt_date(data.get("Dernière  VM", data.get("Dernière VM", ""))),
                        "Examen_Psychotechnique": fmt_date(data.get("Dernier Psy", data.get("Dernière Psy", ""))),
                        "Examen_Professionnel": fmt_date(data.get("Dernière évaluation", data.get("Dernier Eval", ""))),
                        "Engin": engin_val,
                        "Ligne_Site": ligne_site_val,
                    }
    except Exception:
        pass
    return {}


def determine_template_and_defaults(fonction):
    f_lower = fonction.lower().strip()
    if "manœuvre" in f_lower or "manoeuvre" in f_lower or "crmv" in f_lower:
        return "CRMV.xlsx", "E1450, E1400, Z2M, DH400, DM600", "Site Voyageurs Kénitra"
    elif "formation" in f_lower or "cft" in f_lower:
        return "CFT.xlsx", "E1450, E1400, E1250, Z2M, DH400, DM600", "Site Voyageurs Kénitra"
    elif "ligne" in f_lower or "cl" in f_lower:
        return "CL.xlsx", "E1450, E1400, Z2M", ""
    else:
        # Default to CTR (Chef de Trains / Chef de Train)
        return "CTR.xlsx", "E1450, E1400, E1250, Z2M, DH400", ""


if "last_matricule" not in st.session_state:
    st.session_state["last_matricule"] = ""

matricule_search = st.text_input(
    "🔍 Rechercher par Matricule :", placeholder="Ex: 47607A"
)

if matricule_search != st.session_state["last_matricule"]:
    st.session_state["last_matricule"] = matricule_search
    
    official_info = get_official_agent_info(matricule_search) if matricule_search else None
    dates_info = get_agent_dates_and_details(matricule_search) if matricule_search else {}

    if official_info:
        st.session_state["nom"] = official_info["Nom"]
        st.session_state["prenom"] = official_info["Prenom"]
        st.session_state["matricule"] = matricule_search
        st.session_state["fonction"] = official_info["Fonction"]
    else:
        st.session_state["nom"] = ""
        st.session_state["prenom"] = ""
        st.session_state["matricule"] = matricule_search
        st.session_state["fonction"] = "Chef de Trains"

    tmpl_file, def_engins, def_site = determine_template_and_defaults(st.session_state.get("fonction", ""))

    st.session_state["dt_auth"] = dates_info.get("Date_Autorisation", "")
    st.session_state["dt_med"] = dates_info.get("Examen_Medical", "")
    st.session_state["dt_psy"] = dates_info.get("Examen_Psychotechnique", "")
    st.session_state["dt_prof"] = dates_info.get("Examen_Professionnel", "")
    st.session_state["lignes"] = dates_info.get("Ligne_Site", "") if dates_info.get("Ligne_Site") else def_site
    st.session_state["engins"] = dates_info.get("Engin", "") if dates_info.get("Engin") else def_engins

st.session_state.setdefault("nom", "")
st.session_state.setdefault("prenom", "")
st.session_state.setdefault("matricule", matricule_search or "")
st.session_state.setdefault("fonction", "")
st.session_state.setdefault("dt_auth", "")
st.session_state.setdefault("dt_med", "")
st.session_state.setdefault("dt_psy", "")
st.session_state.setdefault("dt_prof", "")
st.session_state.setdefault("lignes", "")
st.session_state.setdefault("engins", "")

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
    st.error(f"⚠️ {search_status} ({matricule_search})")

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
    tmpl_filename, _, _ = determine_template_and_defaults(fonction_input)

    tmpl_path = None
    for f in os.listdir(BASE_DIR):
        if f.lower() == tmpl_filename.lower():
            tmpl_path = os.path.join(BASE_DIR, f)
            break

    if not tmpl_path:
        tmpl_path = os.path.join(BASE_DIR, tmpl_filename)

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

        # أبعاد الصورة بالضبط: 2cm عرض × 1.44cm طول
        target_width_px = int(2.0 * 37.8)   # ~75 px
        target_height_px = int(1.44 * 37.8) # ~54 px

        pil_img = pil_img.resize((target_width_px, target_height_px), PILImage.Resampling.LANCZOS)

        img_temp_path = os.path.join(BASE_DIR, "_temp_photo.png")
        pil_img.save(img_temp_path)

        xl_img = OpenpyxlImage(img_temp_path)
        xl_img.width = target_width_px
        xl_img.height = target_height_px

        sheet.add_image(xl_img, "B5")

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


st.write("")
if st.button("⚡ Générer la Carte"):
    excel_file = generate_custom_excel()

    clean_nom = nom_input.strip() if nom_input.strip() else "Agent"
    custom_filename = f"Carte_{clean_nom}_{matricule_input}.xlsx"

    st.success("✅ Carte générée avec succès !")
    st.download_button(
        label="📥 Télécharger la Carte (Excel)",
        data=excel_file,
        file_name=custom_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
