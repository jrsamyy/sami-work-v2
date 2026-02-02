import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import hashlib
from datetime import datetime

# -------------------------------------------------
# 1. إعداد الاتصال بـ Google Sheets
# -------------------------------------------------
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=scope
    )

    return gspread.authorize(creds)


client = init_connection()
SHEET_NAME = "WorkData"   # اسم ملف Google Sheet
spreadsheet = client.open(SHEET_NAME)

# -------------------------------------------------
# دوال مساعدة
# -------------------------------------------------
def get_data(ws_name):
    sheet = spreadsheet.worksheet(ws_name)
    return pd.DataFrame(sheet.get_all_records())


def add_row(ws_name, row):
    sheet = spreadsheet.worksheet(ws_name)
    sheet.append_row(row)


# -------------------------------------------------
# 2. إعداد الصفحة والتنسيق
# -------------------------------------------------
st.set_page_config(page_title="MyWorkBalance Pro", layout="wide")

st.markdown("""
<style>
.main .block-container { padding: 1rem 1rem !important; }
.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 3.5em;
    font-weight: bold;
    background-color: #007bff;
    color: white;
}
[data-testid="stExpander"] {
    border-radius: 15px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
}
.stMetric {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid #eee;
}
@media (max-width: 480px) {
    .stMetric { margin-bottom: 10px; }
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 3. اللغات
# -------------------------------------------------
LANGS = {
    "العربية": {
        "title": "🔐 نظام إدارة التوازن",
        "login": "دخول",
        "user": "اسم المستخدم",
        "pass": "كلمة المرور",
        "overview": "📊 نظرة عامة",
        "request_leave": "📅 طلب إجازة",
        "overtime": "⏰ الأوفر تايم",
        "lieu": "🎁 Lieu",
        "manage": "⚙️ الإدارة",
        "logout": "خروج",
        "welcome": "أهلاً سامي",
        "annual_rem": "الرصيد السنوي",
        "ot_pending": "الأوفر تايم",
        "lieu_unused": "رصيد Lieu",
        "days": "يوم",
        "hours": "ساعة",
        "note": "ملاحظة",
        "type": "النوع",
        "start": "البداية",
        "end": "النهاية",
        "date": "التاريخ",
        "confirm": "تأكيد",
        "success": "تم بنجاح"
    },
    "Deutsch": {
        "title": "🔐 MyWorkBalance Pro",
        "login": "Login",
        "user": "Benutzer",
        "pass": "Passwort",
        "overview": "📊 Übersicht",
        "request_leave": "📅 Urlaub",
        "overtime": "⏰ Überstunden",
        "lieu": "🎁 Lieu",
        "manage": "⚙️ Verwalten",
        "logout": "Logout",
        "welcome": "Hallo Sami",
        "annual_rem": "Resturlaub",
        "ot_pending": "Offen",
        "lieu_unused": "Lieu-Guthaben",
        "days": "Tage",
        "hours": "Std",
        "note": "Notiz",
        "type": "Typ",
        "start": "Start",
        "end": "Ende",
        "date": "Datum",
        "confirm": "Bestätigen",
        "success": "Erfolgreich"
    }
}

with st.sidebar:
    lang = st.selectbox("Language / لغة", ["العربية", "Deutsch"])
    T = LANGS[lang]
    if lang == "العربية":
        st.markdown(
            "<style>html, body, [class*='st-'] {direction: rtl; text-align: right;}</style>",
            unsafe_allow_html=True
        )

# -------------------------------------------------
# 4. تسجيل الدخول
# -------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title(T["title"])
    with st.form("auth"):
        u = st.text_input(T["user"])
        p = st.text_input(T["pass"], type="password")
        if st.form_submit_button(T["login"]):
            df_u = get_data("users")
            res = df_u[df_u["username"] == u]
            if not res.empty and res.iloc[0]["password"] == hashlib.sha256(p.encode()).hexdigest():
                st.session_state.logged_in = True
                st.session_state.user_id = int(res.iloc[0]["id"])
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة")
    st.stop()

# -------------------------------------------------
# 5. تحميل البيانات
# -------------------------------------------------
uid = st.session_state.user_id

df_l = get_data("leaves")
df_l = df_l[df_l["user_id"] == uid]

df_ot = get_data("overtime")
df_ot = df_ot[df_ot["user_id"] == uid]

df_lieu = get_data("lieu")
df_lieu = df_lieu[df_lieu["user_id"] == uid]

with st.sidebar:
    st.write(f"### {T['welcome']}")
    menu = st.radio("Menu", [
        T["overview"],
        T["request_leave"],
        T["overtime"],
        T["lieu"],
        T["manage"]
    ])
    if st.button(T["logout"]):
        st.session_state.logged_in = False
        st.rerun()

# -------------------------------------------------
# 6. الصفحات
# -------------------------------------------------
if menu == T["overview"]:
    st.header(T["overview"])
    ann_days = df_l[df_l["type"].str.contains("Annual|سنوية|Urlaub", na=False)]["days"].sum()
    c1, c2 = st.columns(2)
    c1.metric(T["annual_rem"], f"{21 - ann_days} {T['days']}")
    c2.metric(T["ot_pending"], f"{df_ot[df_ot['is_paid'] == 0]['hours'].sum()} {T['hours']}")
    st.metric(T["lieu_unused"], f"{df_lieu[df_lieu['is_used'] == 0]['days'].sum()} {T['days']}")

elif menu == T["overtime"]:
    st.header(T["overtime"])
    with st.form("ot"):
        d = st.date_input(T["date"])
        h = st.number_input(T["hours"], min_value=0.5, step=0.5)
        n = st.text_input(T["note"])
        if st.form_submit_button(T["confirm"]):
            add_row("overtime", [int(datetime.now().timestamp()), uid, str(d), h, n, 0])
            st.success(T["success"])
            st.rerun()

elif menu == T["lieu"]:
    st.header(T["lieu"])
    with st.form("li"):
        d = st.date_input(T["date"])
        a = st.number_input(T["days"], min_value=1, step=1)
        n = st.text_area(T["note"])
        if st.form_submit_button(T["confirm"]):
            add_row("lieu", [int(datetime.now().timestamp()), uid, str(d), int(a), n, 0])
            st.success(T["success"])
            st.rerun()

elif menu == T["request_leave"]:
    st.header(T["request_leave"])
    with st.form("lv"):
        tp = st.selectbox(T["type"], ["Annual/سنوية/Urlaub", "Emergency/عارضة", "Sick/مرضية", "Lieu"])
        s = st.date_input(T["start"])
        e = st.date_input(T["end"])
        nt = st.text_area(T["note"])
        if st.form_submit_button(T["confirm"]):
            days = (e - s).days + 1
            add_row("leaves", [int(datetime.now().timestamp()), uid, tp, str(s), str(e), days, nt])
            st.success(T["success"])
            st.rerun()

elif menu == T["manage"]:
    st.header(T["manage"])
    for _, r in df_l.iterrows():
        with st.expander(f"📌 {r['type']} | {r['start']}"):
            st.write(f"{T['days']}: {r['days']}")
            st.write(f"{T['note']}: {r['note']}")
