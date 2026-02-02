import streamlit as st
import pandas as pd
import sqlite3
import hashlib

# --- 1. قاموس الترجمة الشامل لكل اللغات ---
LANGS = {
    "العربية": {
        "title": "🔐 نظام إدارة التوازن العملي",
        "login": "تسجيل دخول",
        "signup": "إنشاء حساب",
        "user": "اسم المستخدم",
        "pass": "كلمة المرور",
        "overview": "📊 نظرة عامة",
        "request_leave": "📅 طلب إجازة",
        "overtime": "⏰ الأوفر تايم",
        "lieu": "🎁 سجل الـ Lieu",
        "manage": "⚙️ إدارة طلباتي",
        "logout": "تسجيل الخروج",
        "welcome": "أهلاً سامي",
        "annual_rem": "رصيد سنوي متبقي",
        "ot_pending": "أوفر تايم (لم يقبض)",
        "lieu_unused": "رصيد Lieu (لم يستخدم)",
        "days": "يوم",
        "hours": "ساعة",
        "status_paid": "تم القبض",
        "status_unpaid": "لم يتم القبض",
        "status_used": "تم الاستخدام",
        "status_unused": "لم يتم الاستخدام",
        "save": "حفظ",
        "delete": "حذف",
        "note": "ملاحظة",
        "type": "النوع",
        "start": "البداية",
        "end": "النهاية",
        "confirm": "تأكيد",
        "success": "تمت العملية بنجاح",
        "error_login": "بيانات الدخول خاطئة",
        "error_user": "اسم المستخدم موجود مسبقاً",
        "lang_sidebar": "القائمة"
    },
    "Deutsch": {
        "title": "🔐 MyWorkBalance Pro",
        "login": "Anmelden",
        "signup": "Registrieren",
        "user": "Benutzername",
        "pass": "Passwort",
        "overview": "📊 Übersicht",
        "request_leave": "📅 Urlaubsantrag",
        "overtime": "⏰ Überstunden",
        "lieu": "🎁 Lieu-Konto",
        "manage": "⚙️ Verwalten",
        "logout": "Abmelden",
        "welcome": "Hallo Sami",
        "annual_rem": "Resturlaub",
        "ot_pending": "Überstunden (offen)",
        "lieu_unused": "Lieu-Guthaben",
        "days": "Tage",
        "hours": "Std",
        "status_paid": "Bezahlt",
        "status_unpaid": "Nicht bezahlt",
        "status_used": "Genommen",
        "status_unused": "Nicht genommen",
        "save": "Speichern",
        "delete": "Löschen",
        "note": "Notiz",
        "type": "Typ",
        "start": "Beginn",
        "end": "Ende",
        "confirm": "Bestätigen",
        "success": "Erfolgreich abgeschlossen",
        "error_login": "Anmeldedaten falsch",
        "error_user": "Benutzername existiert bereits",
        "lang_sidebar": "Menü"
    },
    "English": {
        "title": "🔐 MyWorkBalance Pro",
        "login": "Login",
        "signup": "Sign Up",
        "user": "Username",
        "pass": "Password",
        "overview": "📊 Overview",
        "request_leave": "📅 Request Leave",
        "overtime": "⏰ Overtime",
        "lieu": "🎁 Lieu Records",
        "manage": "⚙️ Manage",
        "logout": "Logout",
        "welcome": "Hello Sami",
        "annual_rem": "Remaining Annual",
        "ot_pending": "Overtime (Pending)",
        "lieu_unused": "Lieu (Unused)",
        "days": "Days",
        "hours": "Hrs",
        "status_paid": "Paid",
        "status_unpaid": "Unpaid",
        "status_used": "Used",
        "status_unused": "Unused",
        "save": "Save",
        "delete": "Delete",
        "note": "Note",
        "type": "Type",
        "start": "Start",
        "end": "End",
        "confirm": "Confirm",
        "success": "Operation Successful",
        "error_login": "Invalid Credentials",
        "error_user": "Username already exists",
        "lang_sidebar": "Menu"
    }
}

# --- 2. الإعدادات واختيار اللغة ---
st.set_page_config(page_title="MyWorkBalance Pro", layout="wide")

with st.sidebar:
    lang_choice = st.selectbox("Language / لغة / Sprache", ["العربية", "Deutsch", "English"])
    T = LANGS[lang_choice]

if lang_choice == "العربية":
    st.markdown("""<style>html, body, [class*="st-"] {direction: rtl; text-align: right;}</style>""", unsafe_allow_html=True)

# --- 3. إدارة قاعدة البيانات ---
def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text

def init_db():
    conn = sqlite3.connect('my_work_final.db', check_same_thread=False)
    cursor = conn.cursor()
    with conn:
        cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS leaves (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, type TEXT, start TEXT, end TEXT, days INTEGER, note TEXT)')
        cursor.execute('''CREATE TABLE IF NOT EXISTS overtime (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                          date TEXT, hours REAL, note TEXT, is_paid INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS lieu_records (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                          date TEXT, days REAL, note TEXT, is_used INTEGER DEFAULT 0)''')
    return conn

conn = init_db()

# --- 4. تسجيل الدخول وإنشاء حساب ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        st.title(T["title"])
        auth_tab = st.tabs([T["login"], T["signup"]])
        with auth_tab[0]:
            with st.form("login_f"):
                u = st.text_input(T["user"])
                p = st.text_input(T["pass"], type="password")
                if st.form_submit_button(T["login"]):
                    res = conn.execute("SELECT id, password FROM users WHERE username=?", (u,)).fetchone()
                    if res and check_hashes(p, res[1]):
                        st.session_state.logged_in, st.session_state.user_id, st.session_state.username = True, res[0], u
                        st.rerun()
                    else: st.error(T["error_login"])
        with auth_tab[1]:
            with st.form("signup_f"):
                nu, np = st.text_input(T["user"]), st.text_input(T["pass"], type="password")
                if st.form_submit_button(T["signup"]):
                    try:
                        with conn: conn.execute("INSERT INTO users (username, password) VALUES (?,?)", (nu, make_hashes(np)))
                        st.success(T["success"])
                    except: st.error(T["error_user"])
    st.stop()

# --- 5. جلب البيانات وحساب الأرصدة ---
uid = st.session_state.user_id
df_l = pd.read_sql(f"SELECT * FROM leaves WHERE user_id={uid}", conn)
df_ot = pd.read_sql(f"SELECT * FROM overtime WHERE user_id={uid}", conn)
df_lieu = pd.read_sql(f"SELECT * FROM lieu_records WHERE user_id={uid}", conn)

rem_ann = 21 - (df_l[df_l['type'].str.contains('Annual|سنوية|Urlaub', na=False)]['days'].sum() if not df_l.empty else 0)
ot_unpaid = df_ot[df_ot['is_paid'] == 0]['hours'].sum() if not df_ot.empty else 0
lieu_unused = df_lieu[df_lieu['is_used'] == 0]['days'].sum() if not df_lieu.empty else 0

# --- 6. القائمة الجانبية ---
with st.sidebar:
    st.divider()
    st.markdown(f"### 👤 {T['welcome']}")
    menu = st.radio(T["lang_sidebar"], [T["overview"], T["request_leave"], T["overtime"], T["lieu"], T["manage"]])
    if st.button(T["logout"]):
        st.session_state.logged_in = False
        st.rerun()

# --- 7. الصفحات ---
if menu == T["overview"]:
    st.header(T["overview"])
    c1, c2, c3 = st.columns(3)
    c1.metric(T["annual_rem"], f"{rem_ann} {T['days']}")
    c2.metric(T["ot_pending"], f"{ot_unpaid} {T['hours']}")
    c3.metric(T["lieu_unused"], f"{lieu_unused} {T['days']}")

elif menu == T["overtime"]:
    st.header(T["overtime"])
    with st.form("ot"):
        d, h = st.date_input(T["start"]), st.number_input(T["hours"], min_value=0.5, step=0.5)
        p = st.selectbox(T["status_paid"] + "?", [T["status_unpaid"], T["status_paid"]])
        n = st.text_input(T["note"])
        if st.form_submit_button(T["confirm"]):
            with conn: conn.execute("INSERT INTO overtime (user_id, date, hours, note, is_paid) VALUES (?,?,?,?,?)",
                                    (uid, str(d), h, n, 1 if p == T["status_paid"] else 0))
            st.rerun()
    for _, row in df_ot.iterrows():
        txt = T["status_paid"] if row['is_paid'] == 1 else T["status_unpaid"]
        with st.expander(f"📌 {row['date']} | {row['hours']} {T['hours']} | {txt}"):
            new_p = st.selectbox(T["status_paid"] + "?", [T["status_unpaid"], T["status_paid"]], index=int(row['is_paid']), key=f"o_{row['id']}")
            if st.button(T["save"], key=f"s_{row['id']}"):
                with conn: conn.execute("UPDATE overtime SET is_paid=? WHERE id=?", (1 if new_p == T["status_paid"] else 0, row['id']))
                st.rerun()
            if st.button(T["delete"], key=f"d_{row['id']}"):
                with conn: conn.execute("DELETE FROM overtime WHERE id=?", (row['id'],))
                st.rerun()

elif menu == T["lieu"]:
    st.header(T["lieu"])
    with st.form("li"):
        d, a = st.date_input(T["start"]), st.number_input(T["days"], min_value=0.5, step=0.5)
        u = st.selectbox(T["status_used"] + "?", [T["status_unused"], T["status_used"]])
        n = st.text_area(T["note"])
        if st.form_submit_button(T["confirm"]):
            with conn: conn.execute("INSERT INTO lieu_records (user_id, date, days, note, is_used) VALUES (?,?,?,?,?)",
                                    (uid, str(d), a, n, 1 if u == T["status_used"] else 0))
            st.rerun()
    for _, row in df_lieu.iterrows():
        txt = T["status_used"] if row['is_used'] == 1 else T["status_unused"]
        with st.expander(f"📌 {row['date']} | {row['days']} {T['days']} | {txt}"):
            nu = st.selectbox(T["status_used"] + "?", [T["status_unused"], T["status_used"]], index=int(row['is_used']), key=f"u_{row['id']}")
            if st.button(T["save"], key=f"ls_{row['id']}"):
                with conn: conn.execute("UPDATE lieu_records SET is_used=? WHERE id=?", (1 if nu == T["status_used"] else 0, row['id']))
                st.rerun()
            if st.button(T["delete"], key=f"ld_{row['id']}"):
                with conn: conn.execute("DELETE FROM lieu_records WHERE id=?", (row['id'],))
                st.rerun()

elif menu == T["request_leave"]:
    st.header(T["request_leave"])
    with st.form("lv"):
        tp = st.selectbox(T["type"], ["Annual/سنوية/Urlaub", "Emergency/عارضة/Notfall", "Sick/مرضية/Krank", "Lieu"])
        s, e = st.date_input(T["start"]), st.date_input(T["end"])
        nt = st.text_area(T["note"])
        if st.form_submit_button(T["confirm"]):
            days = (e - s).days + 1
            if days > 0:
                with conn: conn.execute("INSERT INTO leaves (user_id, type, start, end, days, note) VALUES (?,?,?,?,?,?)", (uid, tp, str(s), str(e), days, nt))
                st.rerun()

elif menu == T["manage"]:
    st.header(T["manage"])
    for _, row in df_l.iterrows():
        with st.expander(f"📌 {row['type']} | {row['start']} → {row['end']}"):
            st.write(f"{T['note']}: {row['note']}")
            if st.button(T["delete"], key=f"l_{row['id']}"):
                with conn: conn.execute("DELETE FROM leaves WHERE id=?", (row['id'],))
                st.rerun()
