# دالة للبحث عن صورة الموظف داخل photo A و photo B فقط
def get_agent_photo(matricule):
    if not matricule:
        return None

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # المجلدات المتاحة حالياً
    photo_folders = [
        os.path.join(base_dir, "photo A"),
        os.path.join(base_dir, "photo B"),
    ]

    clean_target = str(matricule).strip().lower()

    for folder in photo_folders:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                name_without_ext, _ = os.path.splitext(filename)
                # مطابقة دقيقة للاسم بغض النظر عن الحروف الكبيرة/الصغيرة والمسافات
                if name_without_ext.strip().lower() == clean_target:
                    return os.path.join(folder, filename)

    return None
