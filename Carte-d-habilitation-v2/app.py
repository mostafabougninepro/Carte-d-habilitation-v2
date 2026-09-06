def get_agent_data(matricule):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(
        base_dir, "Registre des habilitations EPTC KENITRA 2026.xlsx"
    )

    if not os.path.exists(excel_path):
        return None

    try:
        xl = pd.ExcelFile(excel_path)
        sheets_to_check = ["Conduite", "Formation", "CGPx Conduite"]

        for sheet_name in sheets_to_check:
            if sheet_name in xl.sheet_names:
                df = pd.read_excel(excel_path, sheet_name=sheet_name, header=6)

                # تنظيف أسماء الأعمدة من الفراغات الزائدة
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

                        # 1. البحث إذا كان الاسم والنسب في عمودين منفصلين (Nom) و (Prénom)
                        if "Nom" in data and pd.notnull(data["Nom"]):
                            nom_val = str(data["Nom"]).strip()
                        if "Prénom" in data and pd.notnull(data["Prénom"]):
                            prenom_val = str(data["Prénom"]).strip()

                        # 2. إذا لم يجدهما منفصلين، يبحث في الأعمدة المدمجة (Nom /Prénom, Nom et Prénom, Nom Prénom...)
                        if not nom_val and not prenom_val:
                            for col in df.columns:
                                if "nom" in col.lower():
                                    val = str(data.get(col, "")).strip()
                                    if val and val.lower() != "nan":
                                        parts = val.split(" ", 1)
                                        nom_val = (
                                            parts[0] if len(parts) > 0 else ""
                                        )
                                        prenom_val = (
                                            parts[1] if len(parts) > 1 else ""
                                        )
                                        break

                        # قراءة الوظيفة
                        fonction_val = str(data.get("Fonction", "")).strip()
                        if fonction_val.lower() == "nan":
                            fonction_val = ""

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
                                    "Dernière  VM",
                                    data.get("Dernière VM", ""),
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
                            "Engin": str(
                                data.get("Engin ", data.get("Engin", ""))
                            )
                            if pd.notnull(
                                data.get("Engin ", data.get("Engin", None))
                            )
                            else "",
                            "Ligne_Site": str(
                                data.get(
                                    "Ligne / Site ",
                                    data.get("Ligne / Site", ""),
                                )
                            )
                            if pd.notnull(
                                data.get(
                                    "Ligne / Site ",
                                    data.get("Ligne / Site", None),
                                )
                            )
                            else "",
                        }
    except Exception:
        pass
    return None
