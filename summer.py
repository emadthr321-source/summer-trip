import json
import os
import streamlit as st
import pandas as pd
import urllib.request
import urllib.error

st.set_page_config(
    page_title="رحلة النماص - برنامج التقييم الإبداعي", page_icon="🏔️", layout="wide"
)

# --- إعدادات التخزين السحابي (لتتمكن من الرؤية من أي جهاز مختلف) ---
# يمكنك استبدال الرابط أدناه برابط سحابي مجاني خاص بك (مثلاً JSONBin.io)، أو الاعتماد على الحفظ المحلي التلقائي.
CLOUD_SYNC_ENABLED = False  # اجعلها True إذا أردت تفعيل المزامنة السحابية عبر رابط خارجي
CLOUD_API_URL = ""  # ضع رابط الـ API السحابي هنا إن توفر

# --- تنسيق التصميم العصري (Glassmorphism & Ultra-Clean Dark Mode) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }

    /* خلفية متدرجة حديثة ومريحة للعين */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #111827 0%, #0b0f19 100%);
        background-attachment: fixed;
    }

    /* كروت لوحة الشرف بتأثير الانعكاس الزجاجي (Glassmorphism) */
    .family-card {
        background: rgba(17, 24, 39, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .family-card:hover {
        border-color: rgba(52, 211, 153, 0.4);
        box-shadow: 0 12px 40px 0 rgba(16, 185, 129, 0.15);
        transform: translateY(-4px);
    }

    /* الهيدر الزجاجي الاحترافي */
    .hero-header {
        background: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 28px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* العناوين */
    h1, h2, h3 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
    }

    /* تصميم الأزرار الزجاجية الناعمة */
    .stButton>button {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(8px);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.25);
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        background: rgba(16, 185, 129, 0.15);
        color: #6ee7b7;
        border-color: rgba(52, 211, 153, 0.6);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.25);
    }

    /* الشريط الجانبي */
    [data-testid="stSidebar"] {
        background-color: rgba(13, 19, 34, 0.95);
        backdrop-filter: blur(20px);
        border-left: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_FILE = "data.json"
family_names = ["أسرة المحبة", "أسرة الاخاء", "أسرة الوفاق", "أسرة الوصال"]
league_names = ["دوري كرة القدم", "دوري التنس الأرضي", "دوري الثلاثيات", "دوري كرة الطائرة"]

# --- نظام الحفظ والمزامنة المضمون (لا تفقد أي بيانات أبداً) ---
def load_data():
    # 1. محاولة القراءة من الملف المحلي أولاً
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_data_to_file():
    data = {
        "families": st.session_state.families,
        "cultural_table": st.session_state.cultural_table,
        "festival_logs": st.session_state.festival_logs,
        "social_logs": st.session_state.social_logs,
        "sport_stage": st.session_state.sport_stage,
        "leagues_data": st.session_state.leagues_data,
    }
    # الحفظ المحلي الفوري لضمان عدم الضياع
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    # إذا تم تفعيل السحابة، يتم إرسال التحديثات سحابياً لتراها من أي جهاز
    if CLOUD_SYNC_ENABLED and CLOUD_API_URL:
        try:
            req = urllib.request.Request(
                CLOUD_API_URL,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='PUT'
            )
            urllib.request.urlopen(req)
        except Exception:
            pass

def reset_app():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("تم مسح كافة البيانات وإعادة ضبط المصنع بنجاح!")
    st.rerun()

# تحميل البيانات المحفوظة
saved_data = load_data()

if saved_data and "families" in saved_data:
    if "families" not in st.session_state:
        st.session_state.families = saved_data["families"]
    if "cultural_table" not in st.session_state:
        st.session_state.cultural_table = saved_data.get("cultural_table", [])
    if "festival_logs" not in st.session_state:
        st.session_state.festival_logs = saved_data.get("festival_logs", [])
    if "social_logs" not in st.session_state:
        st.session_state.social_logs = saved_data.get("social_logs", [])
    if "sport_stage" not in st.session_state:
        st.session_state.sport_stage = saved_data.get("sport_stage", "يوم الإثنين")
    if "leagues_data" not in st.session_state:
        st.session_state.leagues_data = saved_data.get("leagues_data", {})
else:
    if "families" not in st.session_state:
        st.session_state.families = {fam: {"score": 0, "logs": [], "history": []} for fam in family_names}
    if "cultural_table" not in st.session_state:
        st.session_state.cultural_table = []
    if "festival_logs" not in st.session_state:
        st.session_state.festival_logs = []
    if "social_logs" not in st.session_state:
        st.session_state.social_logs = []
    if "sport_stage" not in st.session_state:
        st.session_state.sport_stage = "يوم الإثنين"
    if "leagues_data" not in st.session_state:
        st.session_state.leagues_data = {}

for lg in league_names:
    if lg not in st.session_state.leagues_data:
        st.session_state.leagues_data[lg] = {
            fam: {"لعب": 0, "فوز": 0, "تعادل": 0, "خسارة": 0, "له": 0, "عليه": 0, "النقاط": 0} 
            for fam in family_names
        }

def save_history(fam, pts, log_msg):
    st.session_state.families[fam]["history"].append({"points": pts, "log": log_msg})
    save_data_to_file()

def undo_last_action(fam):
    history = st.session_state.families[fam]["history"]
    if history:
        last = history.pop()
        st.session_state.families[fam]["score"] -= last["points"]
        if st.session_state.families[fam]["logs"]:
            st.session_state.families[fam]["logs"].pop(0)
        save_data_to_file()
        st.success(f"تم التراجع عن آخر عملية لـ {fam} بنجاح!")
        st.rerun()
    else:
        st.warning("لا توجد عمليات سابقة للتراجع عنها لهذه الأسرة.")

# واجهة الهيدر الزجاجي
try:
    st.image("header.png", use_container_width=True)
except:
    st.markdown(
        """
        <div class="hero-header">
            <h1 style='margin:0; font-size: 2.2rem; color: #f8fafc !important;'>رحلة النماص الختامية 🏔️</h1>
            <p style='margin:8px 0 0 0; font-size: 1.15rem; color: #34d399;'>شعار الرحلة: صحبة الخير ❤️</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

# الشريط الجانبي الزجاجي
st.sidebar.title("🔐 لوحة التحكم والصلاحيات")
role = st.sidebar.radio("اختر وضع الدخول:", ["طالب (مشاهدة فقط) 👁️", "معلم (تحكم كامل) 🛠️"])

is_teacher = False
if role == "معلم (تحكم كامل) 🛠️":
    pin = st.sidebar.text_input("أدخل رمز المعلم:", type="password")
    if pin == "1234":
        is_teacher = True
        st.sidebar.success("تم تفعيل صلاحيات المعلم بنجاح!")
    else:
        if pin:
            st.sidebar.error("الرمز غير صحيح")

if is_teacher:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠️ الإدارة المتقدمة والبيانات")
    
    if st.sidebar.button("🔄 مزامنة وتحديث النتائج (Sync)"):
        st.rerun()

    st.sidebar.markdown("---")
    reset_confirm = st.sidebar.checkbox("تأكيد الرغبة في مسح كافة البيانات؟")
    if st.sidebar.button("⚠️ إعادة ضبط المصنع (مسح شامل)"):
        if reset_confirm:
            reset_app()
        else:
            st.sidebar.warning("الرجاء تحديد مربع التأكيد أولاً لتفعيل المسح.")

selected_section = st.selectbox(
    "📋 اختر البرنامج المطلوب:",
    [
        "🏆 البرنامج التحفيزي (الترتيب العام والحصيلة)",
        "📖 البرنامج الثقافي",
        "⚽ البرنامج الرياضي",
        "🤝 البرنامج الاجتماعي",
    ]
)

# ================= 1. البرنامج التحفيزي =================
if selected_section == "🏆 البرنامج التحفيزي (الترتيب العام والحصيلة)":
    st.header("🏆 لوحة الشرف للأسر")
    
    sorted_families = sorted(st.session_state.families.items(), key=lambda x: x[1]["score"], reverse=True)

    cols = st.columns(4)
    for idx, (fam_name, data) in enumerate(sorted_families):
        with cols[idx]:
            st.markdown(
                f"""
                <div class="family-card">
                    <h3 style='color:#cbd5e1; margin:0; font-size: 1.1rem;'>#{idx+1} {fam_name}</h3>
                    <h1 style='color:#34d399; margin:12px 0; font-size: 2.6rem;'>{data['score']}</h1>
                    <p style='color:#94a3b8; font-size:0.9rem; margin:0;'>نقطة إجمالية</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.subheader("📊 السجل التفصيلي لنقاط الأسر")
    for fam_name, data in st.session_state.families.items():
        with st.expander(f"سجل {fam_name} (الإجمالي: {data['score']} نقطة)"):
            if data["logs"]:
                for log in data["logs"]:
                    st.markdown(f"<span style='color: #cbd5e1;'>• {log}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='color: #64748b;'>لا توجد سجلات بعد.</span>", unsafe_allow_html=True)

    if is_teacher:
        st.markdown("---")
        st.subheader("🛠️ إضافة نقاط يدوية سريعة")
        col1, col2, col3 = st.columns(3)
        with col1:
            m_fam = st.selectbox("اختر الأسرة:", family_names, key="m_fam")
        with col2:
            m_pts = st.number_input("عدد النقاط:", value=0, key="m_pts")
        with col3:
            m_reason = st.text_input("السبب:", key="m_reason")

        if st.button("إضافة / خصم النقاط"):
            st.session_state.families[m_fam]["score"] += m_pts
            sign = "+" if m_pts >= 0 else ""
            st.session_state.families[m_fam]["logs"].insert(0, f"{sign}{m_pts} نقطة ({m_reason or 'إضافة يدوية'})")
            save_history(m_fam, m_pts, f"{m_pts} نقطة ({m_reason or 'إضافة يدوية'})")
            st.success("تم تحديث النقاط وحفظها بنجاح!")
            st.rerun()

# ================= 2. البرنامج الثقافي =================
elif selected_section == "📖 البرنامج الثقافي":
    st.header("📖 البرنامج الثقافي والمسابقات")

    cul_activity = st.selectbox("اختر المسابقة:", ["حروف مع المتوسط", "ترابيع", "احفظ مافي الصندوق"])

    if is_teacher:
        st.markdown("---")
        st.subheader("🎮 إدارة جولة المسابقة (الفائز يحصل على 3 نقاط)")
        c1, c2 = st.columns(2)
        with c1:
            t1 = st.selectbox("الأسرة الأولى:", family_names, key="cul_t1")
            s1 = st.number_input("نقاط الأولى بالجولة:", min_value=0, value=0, key="cul_s1")
        with c2:
            t2 = st.selectbox("الأسرة الثانية:", family_names, key="cul_t2")
            s2 = st.number_input("نقاط الثانية بالجولة:", min_value=0, value=0, key="cul_s2")

        if st.button("حفظ الجولة ومنح الفائز 3 نقاط"):
            if t1 == t2:
                st.error("لا يمكن أن تتنافس الأسرة ضد نفسها!")
            else:
                winner = t1 if s1 > s2 else (t2 if s2 > s1 else None)
                if winner:
                    st.session_state.families[winner]["score"] += 3
                    st.session_state.families[winner]["logs"].insert(0, f"+3 نقاط (الفوز في {cul_activity})")
                    save_history(winner, 3, f"+3 نقاط (الفوز في {cul_activity})")

                st.session_state.cultural_table.insert(
                    0,
                    {
                        "المسابقة": cul_activity,
                        "الطرف الأول": f"{t1} ({s1})",
                        "الطرف الثاني": f"{t2} ({s2})",
                        "النتيجة / الفائز": f"{winner} (+3 نقاط)" if winner else "تعادل 🤝",
                    },
                )
                save_data_to_file()
                st.success("تم حفظ الجولة بنجاح!")
                st.rerun()

        st.markdown("---")
        st.subheader("↩️ تراجع عن آخر نتيجة ثقافية")
        undo_cul_fam = st.selectbox("اختر الأسرة للتراجع:", family_names, key="undo_cul")
        if st.button("تراجع عن آخر إجراء ثقافي"):
            undo_last_action(undo_cul_fam)

    st.markdown("---")
    st.subheader("📊 جدول نتائج البرنامج الثقافي")
    if st.session_state.cultural_table:
        st.table(st.session_state.cultural_table)
    else:
        st.info("لا توجد مسابقات مسجلة في الجدول حتى الآن.")

# ================= 3. البرنامج الرياضي =================
elif selected_section == "⚽ البرنامج الرياضي":
    st.header("⚽ البرنامج الرياضي والدوريات")

    sport_type = st.selectbox("اختر الدوري:", league_names)

    if is_teacher:
        st.markdown("---")
        if sport_type == "دوري كرة القدم":
            st.subheader(f"⚽ دوري كرة القدم - المرحلة الحالية: [{st.session_state.sport_stage}]")

            col_d1, col_d2, col_d3, col_d4 = st.columns(4)
            with col_d1:
                if st.button("📅 الإثنين"):
                    st.session_state.sport_stage = "يوم الإثنين"
                    save_data_to_file()
                    st.rerun()
            with col_d2:
                if st.button("📅 الثلاثاء"):
                    st.session_state.sport_stage = "يوم الثلاثاء"
                    save_data_to_file()
                    st.rerun()
            with col_d3:
                if st.button("📅 الأربعاء"):
                    st.session_state.sport_stage = "يوم الأربعاء"
                    save_data_to_file()
                    st.rerun()
            with col_d4:
                if st.button("🏆 النهائي"):
                    st.session_state.sport_stage = "النهائي"
                    save_data_to_file()
                    st.rerun()

            if st.session_state.sport_stage in ["يوم الإثنين", "يوم الثلاثاء", "يوم الأربعاء"]:
                s_col1, s_col2 = st.columns(2)
                with s_col1:
                    team_a = st.selectbox("الفريق الأول:", family_names, key="fa")
                    score_a = st.number_input("أهداف الأول:", value=0, key="sa")
                with s_col2:
                    team_b = st.selectbox("الفريق الثاني:", [f for f in family_names if f != team_a], key="fb")
                    score_b = st.number_input("أهداف الثاني:", value=0, key="sb")

                if st.button("اعتماد النتيجة وتحديث الجدول"):
                    table = st.session_state.leagues_data[sport_type]
                    table[team_a]["لعب"] += 1; table[team_a]["له"] += score_a; table[team_a]["عليه"] += score_b
                    table[team_b]["لعب"] += 1; table[team_b]["له"] += score_b; table[team_b]["عليه"] += score_a

                    if score_a > score_b:
                        table[team_a]["فوز"] += 1; table[team_a]["النقاط"] += 3; table[team_b]["خسارة"] += 1
                        st.session_state.families[team_a]["score"] += 3
                        st.session_state.families[team_a]["logs"].insert(0, f"+3 نقاط (فوز في {sport_type})")
                        save_history(team_a, 3, f"+3 نقاط (فوز)")
                    elif score_b > score_a:
                        table[team_b]["فوز"] += 1; table[team_b]["النقاط"] += 3; table[team_a]["خسارة"] += 1
                        st.session_state.families[team_b]["score"] += 3
                        st.session_state.families[team_b]["logs"].insert(0, f"+3 نقاط (فوز في {sport_type})")
                        save_history(team_b, 3, f"+3 نقاط (فوز)")
                    else:
                        table[team_a]["تعادل"] += 1; table[team_a]["النقاط"] += 1
                        table[team_b]["تعادل"] += 1; table[team_b]["النقاط"] += 1
                        st.session_state.families[team_a]["score"] += 1
                        st.session_state.families[team_b]["score"] += 1
                        st.session_state.families[team_a]["logs"].insert(0, f"+1 نقطة (تعادل في {sport_type})")
                        st.session_state.families[team_b]["logs"].insert(0, f"+1 نقطة (تعادل في {sport_type})")
                        save_history(team_a, 1, f"+1 نقطة (تعادل)")
                        save_history(team_b, 1, f"+1 نقطة (تعادل)")
                        
                    save_data_to_file()
                    st.success("تم اعتماد النتيجة وتحديث الترتيب بنجاح!")
                    st.rerun()

            elif st.session_state.sport_stage == "النهائي":
                champ = st.selectbox("اختر البطل الفائز:", family_names)
                champ_pts = st.number_input("نقاط إضافية للبطل:", value=5)
                if st.button("تتويج البطل وإغلاق الدوري"):
                    st.session_state.families[champ]["score"] += champ_pts
                    st.session_state.families[champ]["logs"].insert(0, f"+{champ_pts} نقطة (تتويج دوري كرة القدم)")
                    save_history(champ, champ_pts, f"+{champ_pts} نقطة (تتويج)")
                    st.success(f"تم تتويج {champ} بنجاح!")
                    st.session_state.sport_stage = "يوم الإثنين"
                    save_data_to_file()
                    st.rerun()

        else:
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                team_a = st.selectbox("الفريق الأول:", family_names, key="other_a")
                score_a = st.number_input("أهداف الأول:", value=0, key="other_sa")
            with s_col2:
                team_b = st.selectbox("الفريق الثاني:", [f for f in family_names if f != team_a], key="other_b")
                score_b = st.number_input("أهداف الثاني:", value=0, key="other_sb")

            if st.button("اعتماد النتيجة وتحديث الجدول"):
                table = st.session_state.leagues_data[sport_type]
                table[team_a]["لعب"] += 1; table[team_a]["له"] += score_a; table[team_a]["عليه"] += score_b
                table[team_b]["لعب"] += 1; table[team_b]["له"] += score_b; table[team_b]["عليه"] += score_a

                if score_a > score_b:
                    table[team_a]["فوز"] += 1; table[team_a]["النقاط"] += 3; table[team_b]["خسارة"] += 1
                    st.session_state.families[team_a]["score"] += 3
                    st.session_state.families[team_a]["logs"].insert(0, f"+3 نقاط (فوز في {sport_type})")
                    save_history(team_a, 3, f"+3 نقاط")
                elif score_b > score_a:
                    table[team_b]["فوز"] += 1; table[team_b]["النقاط"] += 3; table[team_a]["خسارة"] += 1
                    st.session_state.families[team_b]["score"] += 3
                    st.session_state.families[team_b]["logs"].insert(0, f"+3 نقاط (فوز في {sport_type})")
                    save_history(team_b, 3, f"+3 نقاط")
                else:
                    table[team_a]["تعادل"] += 1; table[team_a]["النقاط"] += 1
                    table[team_b]["تعادل"] += 1; table[team_b]["النقاط"] += 1
                    st.session_state.families[team_a]["score"] += 1
                    st.session_state.families[team_b]["score"] += 1
                    st.session_state.families[team_a]["logs"].insert(0, f"+1 نقطة (تعادل في {sport_type})")
                    st.session_state.families[team_b]["logs"].insert(0, f"+1 نقطة (تعادل في {sport_type})")
                    save_history(team_a, 1, f"+1 نقطة")
                    save_history(team_b, 1, f"+1 نقطة")
                
                save_data_to_file()
                st.success("تم تحديث الجدول بنجاح!")
                st.rerun()

        st.markdown("---")
        st.subheader("↩️ تراجع عن آخر نتيجة رياضية")
        undo_sport_fam = st.selectbox("اختر الأسرة للتراجع:", family_names, key="undo_sport")
        if st.button("تراجع عن آخر إجراء رياضي"):
            undo_last_action(undo_sport_fam)

    st.markdown("---")
    st.subheader(f"📊 جدول ترتيب {sport_type}")
    league_df = pd.DataFrame.from_dict(st.session_state.leagues_data[sport_type], orient='index')
    league_df = league_df.sort_values(by="النقاط", ascending=False)
    st.table(league_df)

# ================= 4. البرنامج الاجتماعي =================
elif selected_section == "🤝 البرنامج الاجتماعي":
    st.header("🤝 البرنامج الاجتماعي (التقييم اليومي)")

    if is_teacher:
        soc_fam = st.selectbox("اختر الأسرة:", family_names, key="soc_fam")
        soc_cat = st.selectbox(
            "مجال التقييم:",
            [
                "التكميل الأسري (الصيحات - زي موحد - انضباط - تجديد)",
                "المهام الأسرية (تجهيز - خدمة - نظافة - مساعدة)",
            ],
        )
        soc_pts = st.number_input("النقاط الممنوحة (أو الخصم):", value=0, key="soc_pts")
        soc_notes = st.text_area("ملاحظات المعلم:")

        if st.button("حفظ التقييم الاجتماعي"):
            st.session_state.families[soc_fam]["score"] += soc_pts
            sign = "+" if soc_pts >= 0 else ""
            st.session_state.families[soc_fam]["logs"].insert(0, f"{sign}{soc_pts} نقطة (اجتماعي)")
            st.session_state.social_logs.insert(0, f"🤝 {soc_fam}: {soc_pts} نقطة. ({soc_notes})")
            save_history(soc_fam, soc_pts, f"{soc_pts} نقطة (اجتماعي)")
            st.success("تم حفظ التقييم الاجتماعي بنجاح!")
            st.rerun()

    st.markdown("---")
    st.subheader("📜 سجل الملاحظات الاجتماعية")
    if st.session_state.social_logs:
        for slog in st.session_state.social_logs:
            st.write(f"- {slog}")
    else:
        st.info("لا توجد ملاحظات اجتماعية مسجلة بعد.")
