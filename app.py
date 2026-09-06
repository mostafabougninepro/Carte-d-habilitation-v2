import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="تتبع تواريخ الحصص والفحوصات", layout="centered"
)

st.title("📋 تتبع بيانات العون بالسجل")


# دالة قراءة وتجهيز البيانات من Excel
@st.cache_data
def get_agent_data(matricule):
    excel_path = "Registre des habilitations EPTC KENITRA 2026.xlsx"

    # قراءة صفحة Conduite مع ضبط الترويسة (header=6)
    df = pd.read_excel(excel_path, sheet_name="Conduite", header=6)

    # تنظيف رقم التسجيل من الفراغات
    df["Matricule"] = df["Matricule"].astype(str).str.strip()

    # البحث عن الشخص بـ Matricule
    agent = df[df["Matricule"] == str(matricule).strip()]

    if not agent.empty:
        data = agent.iloc[0]

        # دالة تنسيق التواريخ (ترجع نص فارغ "" إذا كان التاريخ غير موجود)
        def fmt_date(val):
            if pd.notnull(val) and str(val) != "NaT" and str(val).strip() != "":
                return pd.to_datetime(val).strftime("%Y-%m-%d")
            return ""

        return {
            "Nom_Prenom": data.get("Nom /Prénom", ""),
            "Fonction": data.get("Fonction", ""),
            "Date_Autorisation": fmt_date(data.get("Date d'autorisation")),
            "Derniere_VM": fmt_date(data.get("Dernière  VM")),
            "Prochaine_VM": fmt_date(data.get("Date prochaine VM  ")),
            "Dernier_Psy": fmt_date(data.get("Dernier Psy")),
            "Prochain_Psy": fmt_date(data.get("Date prochain  Psy")),
            "Derniere_Eval": fmt_date(data.get("Dernière évaluation")),
            "Prochaine_Eval": fmt_date(data.get("Date prochaine évaluation")),
        }
    return None


# إدخال رقم الـ Matricule
matricule_input = st.text_input(
    "أدخل رقم التسجيل (Matricule):", placeholder="مثال: 42685P"
)

if matricule_input:
    agent_info = get_agent_data(matricule_input)

    if agent_info:
        # عرض معلومات الشخص الأساسية
        st.success(f"👤 **Nom & Prénom:** {agent_info['Nom_Prenom']}")
        if agent_info["Fonction"]:
            st.info(f"💼 **Fonction:** {agent_info['Fonction']}")

        st.subheader("📅 التواريخ:")

        # عرض Date d'autorisation فقط إذا كان يحتوي على قيمة
        if agent_info["Date_Autorisation"]:
            st.write(
                f"• **Date d'autorisation:** `{agent_info['Date_Autorisation']}`"
            )

        st.divider()

        # عرض بقية التواريخ فـ أعمدة مرتبة
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="🩺 Dernière VM",
                value=agent_info["Derniere_VM"] or "—",
            )
            if agent_info["Prochaine_VM"]:
                st.caption(f"Prochaine VM: {agent_info['Prochaine_VM']}")

        with col2:
            st.metric(
                label="🧠 Dernier Psy",
                value=agent_info["Dernier_Psy"] or "—",
            )
            if agent_info["Prochain_Psy"]:
                st.caption(f"Prochain Psy: {agent_info['Prochain_Psy']}")

        with col3:
            st.metric(
                label="📝 Dernière Évaluation",
                value=agent_info["Derniere_Eval"] or "—",
            )
            if agent_info["Prochaine_Eval"]:
                st.caption(f"Prochaine Eval: {agent_info['Prochaine_Eval']}")

    else:
        st.error("❌ رقم التسجيل (Matricule) غير موجود فـ الـ Registre.")