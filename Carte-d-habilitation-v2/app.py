# دالة تبحث في photo A أولاً، وإذا لم تجد الصورة تنتقل أوتوماتيكياً إلى photo B
def get_agent_photo(matricule):
    if not matricule or not str(matricule).strip():
        return None

    base_dir = os.path.dirname(os.path.abspath(__file__))
    target = str(matricule).strip().lower()

    # ترتيب البحث: يبدأ بـ photo A ثم photo B
    folders = ["photo A", "photo B"]

    for folder_name in folders:
        folder_path = os.path.join(base_dir, folder_name)

        if os.path.exists(folder_path):
            try:
                for file_name in os.listdir(folder_path):
                    name_part, _ = os.path.splitext(file_name)
                    # إزالة المسافات وتوحيد حالة الأحرف للمطابقة
                    if name_part.strip().lower() == target:
                        return os.path.join(folder_path, file_name)
            except Exception:
                continue

    return None
