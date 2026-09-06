import os
import json
import streamlit as st

# ================= CONFIGURATION & STYLES =================
st.set_page_config(
    page_title="Portail ONCF - Gestion & Accès",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ONCF Theme
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        background-color: #003366;
        color: white;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #002244;
        color: #ffffff;
    }
    .css-18e3th9 { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

# ================= DATABASE GESTION DES UTILISATEURS =================
USERS_FILE = "users_db.json"

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Default initial database
    default_users = {
        "ADMIN": {
            "password": "adminpassword123",
            "role": "Admin",
            "nom": "Administrateur Principal"
        },
        "47607A": {
            "password": "123",
            "role": "Admin",
            "nom": "Mostafa"
        }
    }
    save_users(default_users)
    return default_users

def save_users(users_dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_dict, f, indent=4, ensure_ascii=False)

# Initialisation de la session state
if "users" not in st.session_state:
    st.session_state.users = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.user_role = None
    st.session_state.user_name = None

# ================= AUTHENTIFICATION PAGE =================
def login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #003366;'>🚆 Portail ONCF</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Veuillez vous connecter avec vos identifiants</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            matricule = st.text_input("Matricule / Identifiant").strip()
            password = st.text_input("Mot de passe", type="password").strip()
            submit = st.form_submit_button("Se Connecter")
            
            if submit:
                users = st.session_state.users
                if matricule in users and users[matricule]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = matricule
                    st.session_state.user_role = users[matricule]["role"]
                    st.session_state.user_name = users[matricule]["nom"]
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

# ================= MAIN APP =================
if not st.session_state.logged_in:
    login_page()
else:
    # Sidebar Navigation
    st.sidebar.title("🚆 Menu ONCF")
    st.sidebar.write(f"Bienvenue, **{st.session_state.user_name}**")
    st.sidebar.write((f"Rôle : `{st.session_state.user_role}`"))
    st.sidebar.markdown("---")
    
    menu_options = ["🏠 Accueil / Tableau de Bord"]
    
    # Show user management only for Admins
    if st.session_state.user_role == "Admin":
        menu_options.append("👥 Gestion des Accès")
        
    menu_options.append("🚪 Déconnexion")
    
    choice = st.sidebar.radio("Navigation", menu_options)
    
    if choice == "🏠 Accueil / Tableau de Bord":
        st.title("📊 Tableau de Bord - Portail ONCF")
        st.info("Bienvenue sur votre plateforme de gestion centralisée.")
        
        # Example Dashboard Content
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Statut Système", value="Actif", delta="Stable")
        with col2:
            st.metric(label="Utilisateurs Enregistrés", value=len(st.session_state.users))
        with col3:
            st.metric(label="Session Actuelle", value=st.session_state.current_user)
            
        st.markdown("---")
        st.subheader("💡 Guide Rapide")
        st.write("- Utilisez le menu à gauche pour naviguer.")
        if st.session_state.user_role == "Admin":
            st.write("- En tant qu'**Admin**, vous pouvez ajouter de nouveaux utilisateurs ou modifier leurs rôles depuis l'onglet **Gestion des Accès**.")

    elif choice == "👥 Gestion des Accès":
        if st.session_state.user_role != "Admin":
            st.error("Accès non autorisé.")
        else:
            st.title("👥 Gestion des Accès et Utilisateurs")
            st.write("Créez de nouveaux matricules ou gérez les accès existants.")
            
            tab1, tab2 = st.tabs(["➕ Ajouter un Utilisateur", "📋 Liste des Utilisateurs"])
            
            with tab1:
                with st.form("new_user_form"):
                    new_mat = st.text_input("Nouveau Matricule / Identifiant").strip().upper()
                    new_nom = st.text_input("Nom Complet").strip()
                    new_pwd = st.text_input("Mot de passe", type="password")
                    new_role = st.selectbox("Rôle Système", ["Utilisateur", "Admin"])
                    
                    create_btn = st.form_submit_button("Créer l'utilisateur")
                    
                    if create_btn:
                        if not new_mat or not new_pwd or not new_nom:
                            st.warning("Veuillez remplir tous les champs obligatoires.")
                        elif new_mat in st.session_state.users:
                            st.error("Ce matricule existe déjà !")
                        else:
                            st.session_state.users[new_mat] = {
                                "password": new_pwd,
                                "role": new_role,
                                "nom": new_nom
                            }
                            save_users(st.session_state.users)
                            st.success(f"L'utilisateur {new_mat} ({new_nom}) a été créé avec succès !")
                            
            with tab2:
                st.subheader("Utilisateurs Actuels du Système")
                users_data = []
                for mat, info in st.session_state.users.items():
                    users_data.append({
                        "Matricule": mat,
                        "Nom": info["nom"],
                        "Rôle": info["role"],
                        "Mot de passe": "••••••••" if mat != "ADMIN" else info["password"]
                    })
                st.dataframe(users_data, use_container_width=True)
                
                st.markdown("---")
                st.subheader("🗑️ Supprimer un Utilisateur")
                del_mat = st.selectbox("Sélectionner un Matricule à supprimer", [m for m in st.session_state.users.keys() if m != "ADMIN"])
                if st.button("Supprimer l'utilisateur sélectionné"):
                    if del_mat in st.session_state.users:
                        del st.session_state.users[del_mat]
                        save_users(st.session_state.users)
                        st.success(f"Utilisateur {del_mat} supprimé avec succès !")
                        st.rerun()

    elif choice == "🚪 Déconnexion":
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.rerun()
