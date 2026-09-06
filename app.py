import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.drawing.image import Image as OpenpyxlImage
from PIL import Image as PILImage
import os
import io

st.set_page_config(
    page_title="Système Management Qualité - Carte d'Habilitation",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Système Management Qualité")
st.subheader("Génération des Cartes d'Habilitation ONCF")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):
    return os.path.join(BASE_DIR, filename)

def generate_custom_excel(data, photo_file):
    template_path = get_file_path("Modele_Carte.xlsx")
    
    if not os.path.exists(template_path):
        st.error(f"Le fichier modèle '{template_path}' est introuvable dans le dépôt!")
        return None

    wb = openpyxl.load_workbook(template_path)
    sheet = wb.active

    # Remplissage des données dans le modèle
    sheet["D6"] = data.get("nom_prenom", "")
    sheet["D8"] = data.get("matricule", "")
    sheet["D10"] = data.get("fonction", "")
    sheet["D12"] = data.get("entite", "")
    sheet["D14"] = data.get("date_delivrance", "")
    sheet["D16"] = data.get("date_expiration", "")

    # Traitement et redimensionnement de la photo
    if photo_file is not None:
        try:
            pil_img = PILImage.open(photo_file)
            
            # Conversion des dimensions en Pixels (1 cm ≈ 37.8 pixels)
            # Width: 2 cm -> ~76 px | Height: 1.44 cm -> ~54 px
            target_width_px = int(2.0 * 37.8)
            target_height_px = int(1.44 * 37.8)

            pil_img = pil_img.resize((target_width_px, target_height_px), PILImage.Resampling.LANCZOS)

            img_temp_path = os.path.join(BASE_DIR, "_temp_photo.png")
            pil_img.save(img_temp_path)

            xl_img = OpenpyxlImage(img_temp_path)
            xl_img.width = target_width_px
            xl_img.height = target_height_px

            # Insérer la photo dans la cellule B5
            sheet.add_image(xl_img, "B5")
        except Exception as e:
            st.warning(f"Erreur lors de l'insertion de l'image: {e}")

    output_buffer = io.BytesIO()
    wb.save(output_buffer)
    output_buffer.seek(0)
    
    # Nettoyage du fichier image temporaire
    img_temp_path = os.path.join(BASE_DIR, "_temp_photo.png")
    if os.path.exists(img_temp_path):
        try:
            os.remove(img_temp_path)
        except Exception:
            pass

    return output_buffer

# Formulaire de saisie
with st.form("habilitation_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        nom_prenom = st.text_input("Nom & Prénom")
        matricule = st.text_input("Matricule")
        fonction = st.text_input("Fonction")
        
    with col2:
        entite = st.text_input("Entité / Direction")
        date_delivrance = st.date_input("Date de Délivrance")
        date_expiration = st.date_input("Date d'Expiration")
        
    photo_file = st.file_uploader("Photo de l'agent (PNG/JPG)", type=["png", "jpg", "jpeg"])

    submitted = st.form_submit_button("Générer la Carte Excel")

if submitted:
    if not nom_prenom or not matricule:
        st.error("Veuillez remplir au moins le Nom/Prénom et le Matricule.")
    else:
        user_data = {
            "nom_prenom": nom_prenom,
            "matricule": matricule,
            "fonction": fonction,
            "entite": entite,
            "date_delivrance": str(date_delivrance),
            "date_expiration": str(date_expiration)
        }
        
        excel_data = generate_custom_excel(user_data, photo_file)
        
        if excel_data:
            st.success("Carte générée avec succès!")
            st.download_button(
                label="📥 Télécharger le fichier Excel",
                data=excel_data,
                file_name=f"Carte_Habilitation_{matricule}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
