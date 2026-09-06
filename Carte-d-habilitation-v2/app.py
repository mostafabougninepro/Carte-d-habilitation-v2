=# دالة تشخيصية للبحث عن الصور مع عرض المسارات
def get_agent_photo(matricule):
    if not matricule or not str(matricule).strip():
        return None, "Matricule vide"

    target = str(matricule).strip().lower()

    # طباعة المسارات لتشخيص المشكل فـ Streamlit
    st.write(f"🔍 **مسار الملف الحالي (BASE_DIR):** `{BASE_DIR}`")

    # جمع جميع الملفات والمجلدات الموجودة في المشروع
    all_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            all_files.append(os.path.join(root, f))

    # أضف أيضاً البحث في المجلد الأب تحسباً
    parent_dir = os.path.dirname(BASE_DIR)
    for root, dirs, files in os.walk(parent_dir):
        for f in files:
            all_files.append(os.path.join(root, f))

    # تصفية الملفات المكررة
    all_files = list(set(all_files))

    found_matches = []
    for file_path in all_files:
        filename = os.path.basename(file_path)
        name_part, ext = os.path.splitext(filename)

        # مقارنة اسم الملف بالـ Matricule
        if name_part.strip().lower() == target:
            folder_name = os.path.basename(os.path.dirname(file_path))
            return file_path, f"Photo trouvée dans [{folder_name}] -> {filename}"

    # إذا لم يجد الصورة، سيعرض المجلدات والملفات المكتشفة لمساعدتنا
    st.info(f"📁 إجمالي الملفات التي تم العثور عليها في الخادم: {len(all_files)}")
    return None, "Non trouvée dans les dossiers"
