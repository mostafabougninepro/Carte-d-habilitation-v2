import io
import json
import os
import openpyxl
from openpyxl.drawing.image import Image as OpenpyxlImage
import pandas as pd
from PIL import Image as PILImage
import streamlit as st

# ================= ================= =================
# CONFIGURATION DE LA PAGE
# ================= ================= =================
st.set_page_config(
    page_title="ONCF - Système Management Sécurité",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= ================= =================
# STYLES CSS PERSONNALISÉS (CHARTE GRAPHIQUE ONCF)
# ================= ================= =================
ONCF_CSS = """
<style>
    /* Background & Font */
    .main {
        background-color: #F8FAFC;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header Banner */
    .oncf-header {
        background: linear-gradient(135deg, #0F2C59 0%, #1E40AF 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(15, 44, 89, 0.3);
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .oncf-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin: 0;
        color: #FFFFFF;
    }
    
    .oncf-badge {
        background-color: #E65100;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Login Box Style */
    .login-card {
        background: #FFFFFF;
        padding: 40px;
        border-radius: 16px;
        border-top: 6px solid #E65100;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        margin-top: 20px;
    }
    
    /* Section Cards */
    .css-card {
        background: #FFFFFF;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* Custom Buttons */
    .stButton>button {
        background-color: #0F2C59 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background-color: #E65100 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(230, 81, 0, 0.3) !important;
    }

    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""

st.markdown(ONCF_CSS, unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users_db.json")

# ================= ================= =================
# 1. GESTION DES UTILISATEURS
# ================= ================= =================
def load_users():
    if not os.path.exists(USERS_FILE):
        default_users = {
            "ADMIN": {
                "password": "adminpassword123",
                "role": "Admin",
                "nom": "Administrateur ONCF"
            }
        }
        save_users(default_users)
        return default_users
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# Session State Initialization
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("current_user", None)
st.session_state.setdefault("user_role", None)

# ================= ================= =================
# 2. PAGE DE CONNEXION (LOGIN)
# ================= ================= =================
if not st.session_state["logged_in"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.8, 1])
    
    with col_l2:
        st.markdown("""
            <div class="login-card">
                <div style="text-align: center; margin-bottom: 25px;">
                    <span style="font-size: 50px;">🚆</span>
                    <h2 style="color: #0F2C59; font-weight: 800; margin-top: 10px; margin-bottom: 5px;">ONCF</h2>
                    <p style="color: #64748B; font-weight: 600; font-size: 15px;">Système Management Sécurité</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            input_matricule = st.text_input("Matricule / Identifiant", placeholder="Ex: ADMIN").strip().upper()
            input_password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submit_login = st.form_submit_button("Se Connecter", use_container_width=True)
            
            if submit_login:
                users = load_users()
                if input_matricule in users and users[input_matricule]["password"] == input_password:
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = input_matricule
                    st.session_state["user_role"] = users[input_matricule].get("role", "Utilisateur")
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("❌ Matricule ou mot de passe incorrect.")
    
    st.stop()

# ================= ================= =================
# 3. EN-TÊTE ET NAVIGATION (APPLICATION PRINCIPALE)
# ================= ================= =================

# Banner Header ONCF
st.markdown(f"""
    <div class="oncf-header">
        <div>
            <h1 class="oncf-title">🚆 Office National des Chemins de Fer</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">Système Management Sécurité — Direction Sécurité & Exploitation</p>
        </div>
        <div class="oncf-badge">{st.session_state['user_role']}</div>
    </div>
""", unsafe_allow_html=True)

# User bar & Logout
top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    st.markdown(f"👤 Connecté : **{st.session_state['current_user']}**")
with top_col2:
    if st.button("Déconnexion 🚪", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = None
        st.session_state["user_role"] = None
        st.rerun()

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/d/d5/ONCF_Logo.svg", width=180) if False else None
st.sidebar.markdown("### 📌 Menu Principal")

if st.session_state["user_role"] == "Admin":
    menu = st.sidebar.radio("Navigation :", ["🪪 Cartes d'Habilitation", "👥 Gestion des Utilisateurs"])
else:
    menu = "🪪 Cartes d'Habilitation"

# ================= ================= =================
# 4. GESTION DES UTILISATEURS (ADMIN)
# ================= ================= =================
if menu == "👥 Gestion des Utilisateurs":
    st.subheader("👥 Administration des Accès")
    
    col_u1, col_u2 = st.columns([1, 1])
    
    with col_u1:
        st.markdown("#### ➕ Ajouter un Utilisateur")
        users = load_users()
        with st.form("add_user_form"):
            new_mat = st.text_input("Matricule").strip().upper()
            new_pass = st.text_input("Mot de passe", type="password")
            new_role = st.selectbox("Rôle", ["Utilisateur", "Admin"])
            
            if st.form_submit_button("Enregistrer l'utilisateur", use_container_width=True):
                if not new_mat or not new_pass:
                    st.error("Veuillez remplir tous les champs.")
                elif new_mat in users:
                    st.warning("Cet utilisateur existe déjà.")
                else:
                    users[new_mat] = {"password": new_pass, "role": new_role}
                    save_users(users)
                    st.success(f"Utilisateur {new_mat} ajouté avec succès !")
                    st.rerun()
                    
    with col_u2:
        st.markdown("#### 📋 Utilisateurs Enregistrés")
        users_list = [{"Matricule": m, "Rôle": d.get("role", "Utilisateur")} for m, d in users.items()]
        st.dataframe(pd.DataFrame(users_list), use_container_width=True)
        
    st.stop()

# ================= ================= =================
# 5. MOTEUR ET GENERATION DE CARTES
# ================= ================= =================
st.subheader("🪪 Générateur de Cartes d'Habilitation")

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
                    name_part, _ = os.path.splitext(file_name)
                    if name_part.strip().lower() == target:
                        return os.path.join(folder_path, file_name), f"Photo trouvée [{folder}]"
            except Exception:
                continue
    return None, "Photo non trouvable"

def get_official_agent_info(matricule):
    excel_path = os.path.join(BASE_DIR, "Mis_A_Jour photos.xlsx")
    if not os.path.exists(excel_path):
        return None
    try:
        xl = pd.ExcelFile(excel_path)
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            mle_col = next((c for c in df.columns if str(c).strip().lower() in ["mle", "matricule"]), None)
            if mle_col:
                df[mle_col] = df[mle_col].astype(str).str.strip()
                agent = df[df[mle_col].str.lower() == str(matricule).strip().lower()]
                if not agent.empty:
                    row = agent.iloc[0]
                    return {
                        "Nom": str(row.get("Nom", "")).strip() if pd.notnull(row.get("Nom")) else "",
                        "Prenom": str(row.get("Prénom", "")).strip() if pd.notnull(row.get("Prénom")) else "",
                        "Fonction": str(row.get("Fonction", "")).strip() if pd.notnull(row.get("Fonction")) else ""
                    }
    except Exception:
        pass
    return None

def get_agent_dates_and_details(matricule):
    excel_filename = next((f for f in os.listdir(BASE_DIR) if f.lower().endswith(".xlsx") and "registre" in f.lower()), None)
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
                        return pd.to_datetime(val).strftime("%Y-%m-%d") if pd.notnull(val) and str(val) != "NaT" and str(val).strip() != "" else ""

                    ligne_site_val = next((str(data[c]).strip() for c in df.columns if ("ligne" in c.lower() or "site" in c.lower()) and pd.notnull(data[c]) and str(data[c]).lower() != "nan"), "")
                    engin_val = next((str(data[c]).strip() for c in df.columns if ("engin" in c.lower() or "materiel" in c.lower()) and pd.notnull(data[c]) and str(data[c]).lower() != "nan"), "")

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
        return "CTR.xlsx", "E1450, E1400, E1250, Z2M, DH400", ""

# Search Box Section
st.session_state.setdefault("last_matricule", "")

col_s1, col_s2 = st.columns([3, 1])
with col_s1:
    matricule_search = st.text_input("🔍 Recherche par Matricule Agent :", placeholder="Ex: 47607A")

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

    _, def_engins, def_site = determine_template_and_defaults(st.session_state.get("fonction", ""))
    st.session_state["dt_auth"] = dates_info.get("Date_Autorisation", "")
    st.session_state["dt_med"] = dates_info.get("Examen_Medical", "")
    st.session_state["dt_psy"] = dates_info.get("Examen_Psychotechnique", "")
    st.session_state["dt_prof"] = dates_info.get("Examen_Professionnel", "")
    st.session_state["lignes"] = dates_info.get("Ligne_Site") or def_site
    st.session_state["engins"] = dates_info.get("Engin") or def_engins

# Photo display
found_photo_path, search_status = get_agent_photo(matricule_search)
final_photo_source = None

col_p1, col_p2 = st.columns([1, 3])
with col_p1:
    uploaded_photo = st.file_uploader("Photo d'identité", type=["jpg", "jpeg", "png"])
    if uploaded_photo is not None:
        final_photo_source = uploaded_photo
        st.image(uploaded_photo, caption="Photo importée", width=110)
    elif found_photo_path:
        final_photo_source = found_photo_path
        st.image(found_photo_path, caption=f"✅ Photo trouvée", width=110)
    elif matricule_search.strip():
        st.error("⚠️ Photo non trouvable")

# Form Data
st.markdown("---")
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
    tmpl_path = next((os.path.join(BASE_DIR, f) for f in os.listdir(BASE_DIR) if f.lower() == tmpl_filename.lower()), os.path.join(BASE_DIR, tmpl_filename))

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
        pil_img = PILImage.open(final_photo_source if isinstance(final_photo_source, str) else io.BytesIO(final_photo_source.read()))
        target_w, target_h = int(2.0 * 37.8), int(1.44 * 37.8)
        pil_img = pil_img.resize((target_w, target_h), PILImage.Resampling.LANCZOS)
        
        img_temp_path = os.path.join(BASE_DIR, "_temp_photo.png")
        pil_img.save(img_temp_path)

        xl_img = OpenpyxlImage(img_temp_path)
        xl_img.width, xl_img.height = target_w, target_h
        sheet.add_image(xl_img, "B5")

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

st.markdown("<br>", unsafe_allow_html=True)
if st.button("⚡ Générer la Carte d'Habilitation", use_container_width=True):
    excel_file = generate_custom_excel()
    clean_nom = nom_input.strip() if nom_input.strip() else "Agent"
    
    st.success("✅ Carte générée avec succès !")
    st.download_button(
        label="📥 Télécharger la Carte Excel",
        data=excel_file,
        file_name=f"Carte_ONCF_{clean_nom}_{matricule_input}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
