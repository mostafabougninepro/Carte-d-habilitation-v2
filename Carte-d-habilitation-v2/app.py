# استخراج رمز النموذج (CFT, CL, CTR, CRMV) تلقائياً
modele_code = selected_modele.split("(")[0].strip()

# تجهيز الاسم (إذا كان فارغاً يكتب Agent)
clean_nom = nom_input.strip() if nom_input.strip() else "Agent"

# اسم الملف النهائي: Carte_CFT_JAMALI.xlsx
file_name_custom = f"Carte_{modele_code}_{clean_nom}.xlsx"

st.download_button(
    label="📥 Télécharger la Carte (Excel)",
    data=excel_file,
    file_name=file_name_custom,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
