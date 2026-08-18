import json
import os
import pandas as pd
import streamlit as st
import urllib.error
import urllib.request

st.set_page_config(
    page_title="رحلة النماص - النظام الاحترافي", page_icon="🏔️", layout="wide"
)

# --- إعدادات التخزين السحابي ---
CLOUD_SYNC_ENABLED = False
CLOUD_API_URL = ""

# --- مسار الصورة المخصصة في الهيدر ---
BANNER_IMAGE_PATH = "header.png"

# --- تصميم واجهة واضحة ومتناسقة مريحة للعين (Dark Glassmorphism) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }

    /* خلفية واضحة وداكنة متناسقة مريحة جداً للعين */
    .stApp {
        background-color: #0b1120;
        background-image: 
            radial-gradient(at 0% 0%, rgba(30, 41, 59, 0.7) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(15, 23, 42, 0.9) 0px, transparent 50%);
        background-attachment: fixed;
    }

    /* بطاقات الأسر الزجاجية الواضحة */
    .family-card {
        background: rgba(30, 41, 59, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    .family-card:hover {
        border-color: rgba(52, 211, 153, 0.6);
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(16, 185, 129, 0.2);
        background: rgba(30, 41, 59, 0.95);
    }

    /* عناوين الواجهة */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }

    /* تصميم الأزرار الواضحة والمتناسقة */
    .stButton>button {
        background: #1e293b;
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.4);
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 700;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .stButton>button:hover {
        background: #0f172a;
        color: #6ee7b7;
        border-color: #34d399;
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3);
    }

    /* الشريط الجانبي */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-left: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* تنسيق الجداول والبيانات لتكون واضحة */
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 14px;
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_FILE = "data.json"
family_names = ["أسرة المحبة", "أسرة الاخاء", "أسرة الوفاق", "أسرة الوصال"]
league_names = [
    "دوري كرة القدم",
    "دوري التنس الأرضي",
    "دوري الثلاثيات",
    "دوري كرة الطائرة",
]
football_days = ["يوم الإثنين", "يوم الثلاثاء", "يوم الأربعاء"]


# --- نظام الحفظ المضمون ---
def load_data():
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
      "cultural_history": st.session_state.get("cultural_history", []),
      "festival_logs": st.session_state.festival_logs,
      "social_logs": st.session_state.social_logs,
      "football_stages": st.session_state.get("football_stages", {}),
      "football_history": st.session_state.get("football_history", {}),
      "leagues_data": st.session_state.leagues_data,
      "leagues_history": st.session_state.get("leagues_history", {}),
  }
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

  if CLOUD_SYNC_ENABLED and CLOUD_API_URL:
    try:
      req = urllib.request.Request(
          CLOUD_API_URL,
          data=json.dumps(data).encode("utf-8"),
          headers={"Content-Type": "application/json"},
          method="PUT",
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


# تحميل البيانات المحفوظة تلقائياً
saved_data = load_data()

if saved_data and "families" in saved_data:
  if "families" not in st.session_state:
    st.session_state.families = saved_data["families"]
  if "cultural_table" not in st.session_state:
    st.session_state.cultural_table = saved_data.get("cultural_table", [])
  if "cultural_history" not in st.session_state:
    st.session_state.cultural_history = saved_data.get("cultural_history", [])
  if "festival_logs" not in st.session_state:
    st.session_state.festival_logs = saved_data.get("festival_logs", [])
  if "social_logs" not in st.session_state:
    st.session_state.social_logs = saved_data.get("social_logs", [])

  # هيكل جداول كرة القدم المستقلة للأيام
  if "football_stages" not in st.session_state:
    st.session_state.football_stages = saved_data.get(
        "football_stages",
        {
            day: {
                fam: {
                    "لعب": 0,
                    "فوز": 0,
                    "تعادل": 0,
                    "خسارة": 0,
                    "له": 0,
                    "عليه": 0,
                    "النقاط": 0,
                }
                for fam in family_names
            }
            for day in football_days
        },
    )
  if "football_history" not in st.session_state:
    st.session_state.football_history = saved_data.get(
        "football_history", {day: [] for day in football_days}
    )

  if "leagues_data" not in st.session_state:
    st.session_state.leagues_data = saved_data.get("leagues_data", {})
  if "leagues_history" not in st.session_state:
    st.session_state.leagues_history = saved_data.get("leagues_history", {})
else:
  if "families" not in st.session_state:
    st.session_state.families = {
        fam: {"score": 0, "logs": [], "history": []} for fam in family_names
    }
  if "cultural_table" not in st.session_state:
    st.session_state.cultural_table = []
  if "cultural_history" not in st.session_state:
    st.session_state.cultural_history = []
  if "festival_logs" not in st.session_state:
    st.session_state.festival_logs = []
  if "social_logs" not in st.session_state:
    st.session_state.social_logs = []

  if "football_stages" not in st.session_state:
    st.session_state.football_stages = {
        day: {
            fam: {
                "لعب": 0,
                "فوز": 0,
                "تعادل": 0,
                "خسارة": 0,
                "له": 0,
                "عليه": 0,
                "النقاط": 0,
            }
            for fam in family_names
        }
        for day in football_days
    }
  if "football_history" not in st.session_state:
    st.session_state.football_history = {
        day: [] for day in football_days
    }

  if "leagues_data" not in st.session_state:
    st.session_state.leagues_data = {}
  if "leagues_history" not in st.session_state:
    st.session_state.leagues_history = {}

# التأكد من بقية الدوريات الأخرى
for lg in league_names:
  if lg != "دوري كرة القدم":
    if lg not in st.session_state.leagues_data:
      st.session_state.leagues_data[lg] = {
          fam: {
              "لعب": 0,
              "فوز": 0,
              "تعادل": 0,
              "خسارة": 0,
              "له": 0,
              "عليه": 0,
              "النقاط": 0,
          }
          for fam in family_names
      }
    if lg not in st.session_state.leagues_history:
      st.session_state.leagues_history[lg] = []


def save_history(fam, pts, log_msg):
  st.session_state.families[fam]["history"].append(
      {"points": pts, "log": log_msg}
  )
  save_data_to_file()


# --- دالة التراجع العام عن النقاط الهامشية ---
def undo_last_manual_action(fam):
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


# --- عرض الصورة في الهيدر ---
if os.path.exists(BANNER_IMAGE_PATH):
  st.image(BANNER_IMAGE_PATH, use_container_width=True)
else:
  st.warning("ملف الصورة (header.png) غير موجود في المجلد!")

st.markdown("<br>", unsafe_allow_html=True)

# الشريط الجانبي
st.sidebar.title("🔐 لوحة التحكم والصلاحيات")
role = st.sidebar.radio(
    "اختر وضع الدخول:", ["طالب (مشاهدة فقط) 👁️", "معلم (تحكم كامل) 🛠️"]
)

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
  st.sidebar.subheader("🛠️ الإدارة والبيانات")
  if st.sidebar.button("🔄 مزامنة وتحديث النتائج (Sync)"):
    st.rerun()

  st.sidebar.markdown("---")
  reset_confirm = st.sidebar.checkbox("تأكيد الرغبة في مسح كافة البيانات؟")
  if st.sidebar.button("⚠️ إعادة ضبط المصنع (مسح شامل)"):
    if reset_confirm:
      reset_app()
    else:
      st.sidebar.warning("الرجاء تحديد مربع التأكيد أولاً.")

selected_section = st.selectbox(
    "📋 اختر البرنامج المطلوب:",
    [
        "🏆 البرنامج التحفيزي (الترتيب العام والحصيلة)",
        "📖 البرنامج الثقافي",
        "⚽ البرنامج الرياضي",
        "🤝 البرنامج الاجتماعي",
    ],
)

# ================= 1. البرنامج التحفيزي =================
if selected_section == "🏆 البرنامج التحفيزي (الترتيب العام والحصيلة)":
  st.header("🏆 لوحة الشرف للأسر")

  sorted_families = sorted(
      st.session_state.families.items(),
      key=lambda x: x[1]["score"],
      reverse=True,
  )

  cols = st.columns(4)
  for idx, (fam_name, data) in enumerate(sorted_families):
    with cols[idx]:
      st.markdown(
          f"""
                <div class="family-card">
                    <h3 style='color:#cbd5e1; margin:0; font-size: 1.1rem;'>#{idx + 1} {fam_name}</h3>
                    <h1 style='color:#34d399; margin:14px 0; font-size: 2.8rem; font-weight: 900;'>{data['score']}</h1>
                    <p style='color:#94a3b8; font-size:0.95rem; margin:0;'>نقطة إجمالية</p>
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
          st.markdown(
              f"<span style='color: #f1f5f9; font-size: 1.05rem;'>• {log}</span>",
              unsafe_allow_html=True,
          )
      else:
        st.markdown(
            "<span style='color: #94a3b8;'>لا توجد سجلات بعد.</span>",
            unsafe_allow_html=True,
        )

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
      st.session_state.families[m_fam]["logs"].insert(
          0, f"{sign}{m_pts} نقطة ({m_reason or 'إضافة يدوية'})"
      )
      save_history(m_fam, m_pts, f"{m_pts} نقطة ({m_reason or 'إضافة يدوية'})")
      st.success("تم تحديث النقاط وحفظها بنجاح!")
      st.rerun()

    st.markdown("---")
    st.subheader("⚙️ أدوات التحكم بالبرنامج التحفيزي")
    c_undo, c_reset = st.columns(2)

    with c_undo:
      undo_manual_fam = st.selectbox(
          "تراجع عن آخر إضافة يدوية للأسرة:", family_names, key="undo_man"
      )
      if st.button("↩️ تراجع عن آخر إضافة يدوية"):
        undo_last_manual_action(undo_manual_fam)

    with c_reset:
      st.write("💥 **تصفير النقاط العامة**")
      confirm_incentive_reset = st.checkbox(
          "تأكيد تصفير نقاط الأسر وسجلاتها؟", key="chk_inc"
      )
      if st.button("🔄 إعادة ضبط مصنع للبرنامج التحفيزي"):
        if confirm_incentive_reset:
          for fam in family_names:
            st.session_state.families[fam] = {
                "score": 0,
                "logs": [],
                "history": [],
            }
          save_data_to_file()
          st.success("تم تصفير النقاط والسجلات لجميع الأسر بنجاح!")
          st.rerun()
        else:
          st.warning("يرجى تحديد مربع التأكيد أولاً.")

# ================= 2. البرنامج الثقافي =================
elif selected_section == "📖 البرنامج الثقافي":
  st.header("📖 البرنامج الثقافي والمسابقات")

  cul_activity = st.selectbox(
      "اختر المسابقة:", ["حروف مع المتوسط", "ترابيع", "احفظ مافي الصندوق"]
  )

  if is_teacher:
    st.markdown("---")
    st.subheader("🎮 إدارة جولة المسابقة (الفائز يحصل على 3 نقاط)")
    c1, c2 = st.columns(2)
    with c1:
      t1 = st.selectbox("الطرف الأول:", family_names, key="cul_t1")
      s1 = st.number_input(
          "نقاط الأولى بالجولة:", min_value=0, value=0, key="cul_s1"
      )
    with c2:
      t2 = st.selectbox(
          "الطرف الثاني:",
          [f for f in family_names if f != t1],
          key="cul_t2",
      )
      s2 = st.number_input(
          "نقاط الثانية بالجولة:", min_value=0, value=0, key="cul_s2"
      )

    if st.button("حفظ الجولة ومنح الفائز 3 نقاط"):
      winner = t1 if s1 > s2 else (t2 if s2 > s1 else None)
      if winner:
        st.session_state.families[winner]["score"] += 3
        st.session_state.families[winner]["logs"].insert(
            0, f"+3 نقاط (الفوز في {cul_activity})"
        )
        save_history(winner, 3, f"+3 نقاط (الفوز في {cul_activity})")

      round_data = {
          "المسابقة": cul_activity,
          "الطرف الأول": f"{t1} ({s1})",
          "الطرف الثاني": f"{t2} ({s2})",
          "النتيجة / الفائز": (
              f"{winner} (+3 نقاط)" if winner else "تعادل 🤝"
          ),
          "winner": winner,
      }

      st.session_state.cultural_table.insert(0, round_data)
      st.session_state.cultural_history.append(round_data)

      save_data_to_file()
      st.success("تم حفظ الجولة بنجاح!")
      st.rerun()

    st.markdown("---")
    st.subheader("⚙️ أدوات التحكم بالبرنامج الثقافي")
    c_undo_c, c_reset_c = st.columns(2)

    with c_undo_c:
      st.write("↩️ **التراجع عن آخر جولة ثقافية**")
      if st.button("تراجع عن آخر جولة مسجلة"):
        if st.session_state.cultural_table:
          last_round = st.session_state.cultural_table.pop(0)
          if st.session_state.cultural_history:
            st.session_state.cultural_history.pop()

          winner = last_round.get("winner")
          if winner and winner in st.session_state.families:
            st.session_state.families[winner]["score"] -= 3
            if st.session_state.families[winner]["logs"]:
              st.session_state.families[winner]["logs"].pop(0)

          save_data_to_file()
          st.success("تم التراجع عن آخر جولة ثقافية وخصم النقاط بنجاح!")
          st.rerun()
        else:
          st.warning("لا توجد جولات ثقافية مسجلة للتراجع عنها.")

    with c_reset_c:
      st.write("💥 **تصفير المسابقات الثقافية**")
      chk_cul_reset = st.checkbox(
          "تأكيد مسح كافة نتائج المسابقات الثقافية؟", key="chk_cul"
      )
      if st.button("🔄 إعادة ضبط مصنع للبرنامج الثقافي"):
        if chk_cul_reset:
          st.session_state.cultural_table = []
          st.session_state.cultural_history = []
          save_data_to_file()
          st.success("تم مسح كافة سجلات وجداول المسابقات الثقافية بنجاح!")
          st.rerun()
        else:
          st.warning("يرجى تحديد مربع التأكيد أولاً.")

  st.markdown("---")
  st.subheader("📊 جدول نتائج البرنامج الثقافي")
  if st.session_state.cultural_table:
    display_table = [
        {
            "المسابقة": r["المسابقة"],
            "الطرف الأول": r["الطرف الأول"],
            "الطرف الثاني": r["الطرف الثاني"],
            "النتيجة / الفائز": r["النتيجة / الفائز"],
        }
        for r in st.session_state.cultural_table
    ]
    st.table(display_table)
  else:
    st.info("لا توجد مسابقات مسجلة في الجدول حتى الآن.")

# ================= 3. البرنامج الرياضي =================
elif selected_section == "⚽ البرنامج الرياضي":
  st.header("⚽ البرنامج الرياضي والدوريات")

  sport_type = st.selectbox("اختر الدوري:", league_names)

  # --- دوري كرة القدم بجداول مستقلة تماماً لكل يوم ---
  if sport_type == "دوري كرة القدم":
    st.subheader("⚽ دوري كرة القدم - جداول مستقلة للأيام")

    selected_football_day = st.selectbox(
        "اختر اليوم لعرض وتعديل جدوله:", football_days
    )

    if is_teacher:
      st.markdown("---")
      st.markdown(f"**تسجيل مباراة جديدة في [{selected_football_day}]**")
      s_col1, s_col2 = st.columns(2)
      with s_col1:
        team_a = st.selectbox("الفريق الأول:", family_names, key="f_team_a")
        score_a = st.number_input("أهداف الأول:", value=0, key="f_score_a")
      with s_col2:
        team_b = st.selectbox(
            "الفريق الثاني:",
            [f for f in family_names if f != team_a],
            key="f_team_b",
        )
        score_b = st.number_input("أهداف الثاني:", value=0, key="f_score_b")

      if st.button(f"اعتماد نتيجة المباراة لـ ({selected_football_day})"):
        table = st.session_state.football_stages[selected_football_day]
        table[team_a]["لعب"] += 1
        table[team_a]["له"] += score_a
        table[team_a]["عليه"] += score_b

        table[team_b]["لعب"] += 1
        table[team_b]["له"] += score_b
        table[team_b]["عليه"] += score_a

        pts_a, pts_b = 0, 0
        res_type = "draw"

        if score_a > score_b:
          table[team_a]["فوز"] += 1
          table[team_a]["النقاط"] += 3
          table[team_b]["خسارة"] += 1
          st.session_state.families[team_a]["score"] += 3
          st.session_state.families[team_a]["logs"].insert(
              0, f"+3 نقاط (فوز في كرة القدم - {selected_football_day})"
          )
          save_history(team_a, 3, f"+3 نقاط (فوز {selected_football_day})")
          pts_a = 3
          res_type = "win_a"
        elif score_b > score_a:
          table[team_b]["فوز"] += 1
          table[team_b]["النقاط"] += 3
          table[team_a]["خسارة"] += 1
          st.session_state.families[team_b]["score"] += 3
          st.session_state.families[team_b]["logs"].insert(
              0, f"+3 نقاط (فوز في كرة القدم - {selected_football_day})"
          )
          save_history(team_b, 3, f"+3 نقاط (فوز {selected_football_day})")
          pts_b = 3
          res_type = "win_b"
        else:
          table[team_a]["تعادل"] += 1
          table[team_a]["النقاط"] += 1
          table[team_b]["تعادل"] += 1
          table[team_b]["النقاط"] += 1
          st.session_state.families[team_a]["score"] += 1
          st.session_state.families[team_b]["score"] += 1
          st.session_state.families[team_a]["logs"].insert(
              0, f"+1 نقطة (تعادل في كرة القدم - {selected_football_day})"
          )
          st.session_state.families[team_b]["logs"].insert(
              0, f"+1 نقطة (تعادل في كرة القدم - {selected_football_day})"
          )
          save_history(
              team_a, 1, f"+1 نقطة (تعادل {selected_football_day})"
          )
          save_history(
              team_b, 1, f"+1 نقطة (تعادل {selected_football_day})"
          )
          pts_a, pts_b = 1, 1

        st.session_state.football_history[selected_football_day].append({
            "team_a": team_a,
            "team_b": team_b,
            "score_a": score_a,
            "score_b": score_b,
            "pts_a": pts_a,
            "pts_b": pts_b,
            "res_type": res_type,
        })

        save_data_to_file()
        st.success(
            f"تم اعتماد وتحديث جدول [{selected_football_day}] بنجاح!"
        )
        st.rerun()

      st.markdown("---")
      st.subheader(f"⚙️ أدوات التحكم بـ ({selected_football_day})")
      c_undo_f, c_reset_f = st.columns(2)

      with c_undo_f:
        st.write(f"↩️ **تراجع عن آخر مباراة في ({selected_football_day})**")
        if st.button(f"تراجع عن آخر مباراة"):
          history = st.session_state.football_history[selected_football_day]
          if history:
            last_match = history.pop()
            ta = last_match["team_a"]
            tb = last_match["team_b"]
            sa = last_match["score_a"]
            sb = last_match["score_b"]
            res = last_match["res_type"]

            table = st.session_state.football_stages[selected_football_day]
            table[ta]["لعب"] -= 1
            table[ta]["له"] -= sa
            table[ta]["عليه"] -= sb

            table[tb]["لعب"] -= 1
            table[tb]["له"] -= sb
            table[tb]["عليه"] -= sa

            if res == "win_a":
              table[ta]["فوز"] -= 1
              table[ta]["النقاط"] -= 3
              table[tb]["خسارة"] -= 1
              st.session_state.families[ta]["score"] -= 3
              if st.session_state.families[ta]["logs"]:
                st.session_state.families[ta]["logs"].pop(0)
            elif res == "win_b":
              table[tb]["فوز"] -= 1
              table[tb]["النقاط"] -= 3
              table[ta]["خسارة"] -= 1
              st.session_state.families[tb]["score"] -= 3
              if st.session_state.families[tb]["logs"]:
                st.session_state.families[tb]["logs"].pop(0)
            else:
              table[ta]["تعادل"] -= 1
              table[ta]["النقاط"] -= 1
              table[tb]["تعادل"] -= 1
              table[tb]["النقاط"] -= 1
              st.session_state.families[ta]["score"] -= 1
              st.session_state.families[tb]["score"] -= 1
              if st.session_state.families[ta]["logs"]:
                st.session_state.families[ta]["logs"].pop(0)
              if st.session_state.families[tb]["logs"]:
                st.session_state.families[tb]["logs"].pop(0)

            save_data_to_file()
            st.success("تم التراجع عن المباراة وإلغاء نقاطها بنجاح!")
            st.rerun()
          else:
            st.warning(f"لا توجد مباريات مسجلة في {selected_football_day}.")

      with c_reset_f:
        st.write(f"💥 **تصفير جدول ({selected_football_day})**")
        chk_day_reset = st.checkbox(
            f"تأكيد تصفير جدول {selected_football_day} فقط؟",
            key=f"chk_{selected_football_day}",
        )
        if st.button(f"🔄 إعادة ضبط جدول ({selected_football_day})"):
          if chk_day_reset:
            st.session_state.football_stages[selected_football_day] = {
                fam: {
                    "لعب": 0,
                    "فوز": 0,
                    "تعادل": 0,
                    "خسارة": 0,
                    "له": 0,
                    "عليه": 0,
                    "النقاط": 0,
                }
                for fam in family_names
            }
            st.session_state.football_history[selected_football_day] = []
            save_data_to_file()
            st.success(f"تمت إعادة ضبط جدول {selected_football_day} بنجاح!")
            st.rerun()
          else:
            st.warning("يرجى تحديد مربع التأكيد أولاً.")

    st.markdown("---")
    st.subheader(
        f"📊 جدول ترتيب دوري كرة القدم لـ [{selected_football_day}]"
    )
    day_df = pd.DataFrame.from_dict(
        st.session_state.football_stages[selected_football_day], orient="index"
    )
    day_df = day_df.sort_values(by="النقاط", ascending=False)
    st.table(day_df)

  # --- باقي الدوريات الأخرى ---
  else:
    if is_teacher:
      st.markdown("---")
      s_col1, s_col2 = st.columns(2)
      with s_col1:
        team_a = st.selectbox("الفريق الأول:", family_names, key="other_a")
        score_a = st.number_input("أهداف الأول:", value=0, key="other_sa")
      with s_col2:
        team_b = st.selectbox(
            "الفريق الثاني:",
            [f for f in family_names if f != team_a],
            key="other_b",
        )
        score_b = st.number_input("أهداف الثاني:", value=0, key="other_sb")

      if st.button("اعتماد النتيجة وتحديث الجدول"):
        table = st.session_state.leagues_data[sport_type]
        table[team_a]["لعب"] += 1
        table[team_a]["له"] += score_a
        table[team_a]["عليه"] += score_b

        table[team_b]["لعب"] += 1
        table[team_b]["له"] += score_b
        table[team_b]["عليه"] += score_a

        pts_a, pts_b = 0, 0
        res_type = "draw"

        if score_a > score_b:
          table[team_a]["فوز"] += 1
          table[team_a]["النقاط"] += 3
          table[team_b]["خسارة"] += 1
          st.session_state.families[team_a]["score"] += 3
          st.session_state.families[team_a]["logs"].insert(
              0, f"+3 نقاط (فوز في {sport_type})"
          )
          save_history(team_a, 3, "+3 نقاط")
          pts_a = 3
          res_type = "win_a"
        elif score_b > score_a:
          table[team_b]["فوز"] += 1
          table[team_b]["النقاط"] += 3
          table[team_a]["خسارة"] += 1
          st.session_state.families[team_b]["score"] += 3
          st.session_state.families[team_b]["logs"].insert(
              0, f"+3 نقاط (فوز في {sport_type})"
          )
          save_history(team_b, 3, "+3 نقاط")
          pts_b = 3
          res_type = "win_b"
        else:
          table[team_a]["تعادل"] += 1
          table[team_a]["النقاط"] += 1
          table[team_b]["تعادل"] += 1
          table[team_b]["النقاط"] += 1
          st.session_state.families[team_a]["score"] += 1
          st.session_state.families[team_b]["score"] += 1
          st.session_state.families[team_a]["logs"].insert(
              0, f"+1 نقطة (تعادل في {sport_type})"
          )
          st.session_state.families[team_b]["logs"].insert(
              0, f"+1 نقطة (تعادل في {sport_type})"
          )
          save_history(team_a, 1, "+1 نقطة")
          save_history(team_b, 1, "+1 نقطة")
          pts_a, pts_b = 1, 1

        st.session_state.leagues_history[sport_type].append({
            "team_a": team_a,
            "team_b": team_b,
            "score_a": score_a,
            "score_b": score_b,
            "pts_a": pts_a,
            "pts_b": pts_b,
            "res_type": res_type,
        })

        save_data_to_file()
        st.success("تم تحديث الجدول بنجاح!")
        st.rerun()

      st.markdown("---")
      st.subheader(f"⚙️ أدوات التحكم بـ ({sport_type})")
      c_undo_s, c_reset_s = st.columns(2)

      with c_undo_s:
        st.write("↩️ **تراجع عن آخر مباراة في هذا الدوري**")
        if st.button("تراجع عن آخر مباراة مسجلة"):
          history = st.session_state.leagues_history[sport_type]
          if history:
            last_match = history.pop()
            ta = last_match["team_a"]
            tb = last_match["team_b"]
            sa = last_match["score_a"]
            sb = last_match["score_b"]
            res = last_match["res_type"]

            table = st.session_state.leagues_data[sport_type]
            table[ta]["لعب"] -= 1
            table[ta]["له"] -= sa
            table[ta]["عليه"] -= sb

            table[tb]["لعب"] -= 1
            table[tb]["له"] -= sb
            table[tb]["عليه"] -= sa

            if res == "win_a":
              table[ta]["فوز"] -= 1
              table[ta]["النقاط"] -= 3
              table[tb]["خسارة"] -= 1
              st.session_state.families[ta]["score"] -= 3
              if st.session_state.families[ta]["logs"]:
                st.session_state.families[ta]["logs"].pop(0)
            elif res == "win_b":
              table[tb]["فوز"] -= 1
              table[tb]["النقاط"] -= 3
              table[ta]["خسارة"] -= 1
              st.session_state.families[tb]["score"] -= 3
              if st.session_state.families[tb]["logs"]:
                st.session_state.families[tb]["logs"].pop(0)
            else:
              table[ta]["تعادل"] -= 1
              table[ta]["النقاط"] -= 1
              table[tb]["تعادل"] -= 1
              table[tb]["النقاط"] -= 1
              st.session_state.families[ta]["score"] -= 1
              st.session_state.families[tb]["score"] -= 1
              if st.session_state.families[ta]["logs"]:
                st.session_state.families[ta]["logs"].pop(0)
              if st.session_state.families[tb]["logs"]:
                st.session_state.families[tb]["logs"].pop(0)

            save_data_to_file()
            st.success("تم التراجع عن المباراة بنجاح!")
            st.rerun()
          else:
            st.warning("لا توجد مباريات سابقة للتراجع عنها في هذا الدوري.")

      with c_reset_s:
        st.write("💥 **تصفير هذا الدوري**")
        chk_sp_reset = st.checkbox(
            f"تأكيد تصفير {sport_type} فقط؟", key="chk_sp"
        )
        if st.button(f"🔄 إعادة ضبط مصنع لـ ({sport_type})"):
          if chk_sp_reset:
            st.session_state.leagues_data[sport_type] = {
                fam: {
                    "لعب": 0,
                    "فوز": 0,
                    "تعادل": 0,
                    "خسارة": 0,
                    "له": 0,
                    "عليه": 0,
                    "النقاط": 0,
                }
                for fam in family_names
            }
            st.session_state.leagues_history[sport_type] = []
            save_data_to_file()
            st.success(f"تمت إعادة ضبط جدول {sport_type} بنجاح!")
            st.rerun()
          else:
            st.warning("يرجى تحديد مربع التأكيد أولاً.")

    st.markdown("---")
    st.subheader(f"📊 جدول ترتيب {sport_type}")
    league_df = pd.DataFrame.from_dict(
        st.session_state.leagues_data[sport_type], orient="index"
    )
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
    soc_pts = st.number_input(
        "النقاط الممنوحة (أو الخصم):", value=0, key="soc_pts"
    )
    soc_notes = st.text_area("ملاحظات المعلم:")

    if st.button("حفظ التقييم الاجتماعي"):
      st.session_state.families[soc_fam]["score"] += soc_pts
      sign = "+" if soc_pts >= 0 else ""
      st.session_state.families[soc_fam]["logs"].insert(
          0, f"{sign}{soc_pts} نقطة (اجتماعي)"
      )

      log_entry = {
          "fam": soc_fam,
          "pts": soc_pts,
          "text": f"🤝 {soc_fam}: {soc_pts} نقطة. ({soc_notes})",
      }
      st.session_state.social_logs.insert(0, log_entry)

      save_history(soc_fam, soc_pts, f"{soc_pts} نقطة (اجتماعي)")
      st.success("تم حفظ التقييم الاجتماعي بنجاح!")
      st.rerun()

    st.markdown("---")
    st.subheader("⚙️ أدوات التحكم بالبرنامج الاجتماعي")
    c_undo_soc, c_reset_soc = st.columns(2)

    with c_undo_soc:
      st.write("↩️ **التراجع عن آخر تقييم اجتماعي**")
      if st.button("تراجع عن آخر ملاحظة اجتماعية"):
        if st.session_state.social_logs:
          last_soc = st.session_state.social_logs.pop(0)

          if isinstance(last_soc, dict):
            sfam = last_soc["fam"]
            spts = last_soc["pts"]
            st.session_state.families[sfam]["score"] -= spts
            if st.session_state.families[sfam]["logs"]:
              st.session_state.families[sfam]["logs"].pop(0)

          save_data_to_file()
          st.success("تم التراجع عن آخر ملاحظة اجتماعية بنجاح!")
          st.rerun()
        else:
          st.warning("لا توجد ملاحظات اجتماعية للتراجع عنها.")

    with c_reset_soc:
      st.write("💥 **تصفير السجل الاجتماعي**")
      chk_soc_reset = st.checkbox(
          "تأكيد مسح كافة الملاحظات الاجتماعية؟", key="chk_soc"
      )
      if st.button("🔄 إعادة ضبط مصنع للبرنامج الاجتماعي"):
        if chk_soc_reset:
          st.session_state.social_logs = []
          save_data_to_file()
          st.success("تم مسح كافة الملاحظات والتقييمات الاجتماعية بنجاح!")
          st.rerun()
        else:
          st.warning("يرجى تحديد مربع التأكيد أولاً.")

  st.markdown("---")
  st.subheader("📜 سجل الملاحظات الاجتماعية")
  if st.session_state.social_logs:
    for slog in st.session_state.social_logs:
      if isinstance(slog, dict):
        st.write(f"- {slog['text']}")
      else:
        st.write(f"- {slog}")
  else:
    st.info("لا توجد ملاحظات اجتماعية مسجلة بعد.")
