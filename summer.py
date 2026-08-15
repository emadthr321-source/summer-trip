import json
import os
import streamlit as st

st.set_page_config(
    page_title="رحلة النماص - برنامج التقييم", page_icon="🏔️", layout="wide"
)

# اسم ملف الحفظ التلقائي
DATA_FILE = "data.json"

# أسماء الأسر الجديدة
family_names = ["أسرة المحبة", "أسرة الاخاء", "أسرة الوفاق", "أسرة الوصال"]


# دوال حفظ وتحميل البيانات من ملف
def load_data():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return None
  return None


def save_data_to_file():
  data = {
      "families": st.session_state.families,
      "cultural_table": st.session_state.cultural_table,
      "festival_logs": st.session_state.festival_logs,
      "social_logs": st.session_state.social_logs,
      "sport_stage": st.session_state.sport_stage,
  }
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# استرجاع البيانات المحفوظة إن وجدت
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
else:
  # التهيئة الافتراضية لو لم يجد ملف حفظ
  if "families" not in st.session_state:
    st.session_state.families = {
        fam: {"score": 0, "logs": [], "history": []} for fam in family_names
    }
  if "cultural_table" not in st.session_state:
    st.session_state.cultural_table = []
  if "festival_logs" not in st.session_state:
    st.session_state.festival_logs = []
  if "social_logs" not in st.session_state:
    st.session_state.social_logs = []
  if "sport_stage" not in st.session_state:
    st.session_state.sport_stage = "يوم الإثنين"


# دالة لتسجيل الحالة وتتبعها لكل أسرة مع الحفظ التلقائي
def save_history(fam, pts, log_msg):
  st.session_state.families[fam]["history"].append(
      {"points": pts, "log": log_msg}
  )
  save_data_to_file()


# دالة العودة للسابق (التراجع)
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


# عرض صورة الشعار في الهيدر
try:
  st.image("header.png", use_container_width=True)
except:
  st.markdown(
      """
        <div style='background: linear-gradient(135deg, #1b4d3e, #2c6b56); padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px;'>
            <h1 style='margin:0; font-size: 2rem;'>رحلة النماص الختامية 🏔️</h1>
            <p style='margin:5px 0 0 0; font-size: 1.1rem;'>شعار الرحلة: صحبة الخير ❤️</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

# الشريط الجانبي لتحديد الصلاحيات
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

# القائمة المنسدلة للتنقل
st.markdown("### 📋 اختر البرنامج المطلوب:")
selected_section = st.selectbox(
    "",
    [
        "🏆 البرنامج التحفيزي (الترتيب العام والحصيلة)",
        "📖 البرنامج الثقافي",
        "⚽ البرنامج الرياضي",
        "🤝 البرنامج الاجتماعي",
    ],
    label_visibility="collapsed",
)

# ================= 1. البرنامج التحفيزي =================
if selected_section == "🏆 البرنامج التحفيزي (الترتيب العام والحصيلة)":
  st.header("🏆 البرنامج التحفيزي (لوحة الشرف للأسر)")
  st.write("الحصيلة العامة لجميع نقاط الأسر المحدثة لحظياً:")

  sorted_families = sorted(
      st.session_state.families.items(), key=lambda x: x[1]["score"], reverse=True
  )

  cols = st.columns(4)
  for idx, (fam_name, data) in enumerate(sorted_families):
    with cols[idx]:
      st.markdown(
          f"""
                <div style='background:#f8fafc; border:2px solid #e2e8f0; padding:15px; border-radius:10px; text-align:center;'>
                    <h3 style='color:#1b4d3e; margin:0;'>#{idx+1} {fam_name}</h3>
                    <h1 style='color:#d4af37; margin:10px 0;'>{data['score']}</h1>
                    <p style='color:#7f8c8d; font-size:0.85rem;'>نقطة</p>
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
          st.write(f"• {log}")
      else:
        st.write("لا توجد سجلات بعد.")

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
      t1 = st.selectbox("الأسرة الأولى:", family_names, key="cul_t1")
      s1 = st.number_input("نقاط الأولى بالجولة:", min_value=0, value=0, key="cul_s1")
    with c2:
      t2 = st.selectbox("الأسرة الثانية:", family_names, key="cul_t2")
      s2 = st.number_input("نقاط الثانية بالجولة:", min_value=0, value=0, key="cul_s2")

    if st.button("حفظ الجولة ومنح الفائز 3 نقاط والانتقال للتالية"):
      if t1 == t2:
        st.error("لا يمكن أن تتنافس الأسرة ضد نفسها!")
      else:
        winner = t1 if s1 > s2 else (t2 if s2 > s1 else None)
        if winner:
          st.session_state.families[winner]["score"] += 3
          st.session_state.families[winner]["logs"].insert(
              0, f"+3 نقاط (الفوز في {cul_activity})"
          )
          save_history(winner, 3, f"+3 نقاط (الفوز في {cul_activity})")

        st.session_state.cultural_table.insert(
            0,
            {
                "المسابقة": cul_activity,
                "الطرف الأول": f"{t1} ({s1})",
                "الطرف الثاني": f"{t2} ({s2})",
                "النتيجة / الفائز": (
                    f"{winner} (+3 نقاط)" if winner else "تعادل 🤝"
                ),
            },
        )
        save_data_to_file()
        st.success("تم حفظ الجولة بنجاح!")
        st.rerun()

    st.markdown("---")
    st.subheader("↩️ تراجع عن آخر نتيجة في الدوري الثقافي")
    undo_cul_fam = st.selectbox(
        "اختر الأسرة للتراجع عن آخر نقطة أضيفت لها ثقافياً:",
        family_names,
        key="undo_cul",
    )
    if st.button("تراجع عن آخر إجراء للأسرة المحددة ثقافياً"):
      undo_last_action(undo_cul_fam)

    st.markdown("---")
    st.subheader("⚡ الفاصل الحركي الثقافي")
    k_col1, k_col2 = st.columns(2)
    with k_col1:
      k_fam = st.selectbox("الأسرة:", family_names, key="k_fam")
    with k_col2:
      k_pts = st.number_input(
          "النقاط المحصودة:", min_value=0, value=0, key="k_pts"
      )
    if st.button("تسجيل نقاط الفاصل الحركي"):
      st.session_state.families[k_fam]["score"] += k_pts
      st.session_state.families[k_fam]["logs"].insert(
          0, f"+{k_pts} نقطة (فاصل حركي ثقافي)"
      )
      save_history(k_fam, k_pts, f"+{k_pts} نقطة (فاصل حركي ثقافي)")
      st.success("تم تسجيل الفاصل وحفظه بنجاح!")
      st.rerun()

  st.markdown("---")
  st.subheader("📊 جدول نتائج البرنامج الثقافي")
  if st.session_state.cultural_table:
    st.table(st.session_state.cultural_table)
  else:
    st.info("لا توجد مسابقات مسجلة في الجدول حتى الآن.")

# ================= 3. البرنامج الرياضي =================
elif selected_section == "⚽ البرنامج الرياضي":
  st.header("⚽ البرنامج الرياضي والدوريات")

  sport_type = st.selectbox(
      "اختر الدوري:",
      ["دوري كرة القدم", "دوري التنس الأرضي", "دوري الثلاثيات", "دوري كرة الطائرة"],
  )

  if is_teacher:
    st.markdown("---")
    if sport_type == "دوري كرة القدم":
      st.subheader(
          f"⚽ دوري كرة القدم - المرحلة الحالية: [{st.session_state.sport_stage}]"
      )

      col_d1, col_d2, col_d3, col_d4 = st.columns(4)
      with col_d1:
        if st.button("📅 يوم الإثنين"):
          st.session_state.sport_stage = "يوم الإثنين"
          save_data_to_file()
          st.rerun()
      with col_d2:
        if st.button("📅 يوم الثلاثاء"):
          st.session_state.sport_stage = "يوم الثلاثاء"
          save_data_to_file()
          st.rerun()
      with col_d3:
        if st.button("📅 يوم الأربعاء"):
          st.session_state.sport_stage = "يوم الأربعاء"
          save_data_to_file()
          st.rerun()
      with col_d4:
        if st.button("🏆 النهائي"):
          st.session_state.sport_stage = "النهائي"
          save_data_to_file()
          st.rerun()

      if st.session_state.sport_stage in [
          "يوم الإثنين",
          "يوم الثلاثاء",
          "يوم الأربعاء",
      ]:
        st.info(
            f"تسجيل مباريات ونتائج ({st.session_state.sport_stage}) - الفائز"
            " يحصل على 3 نقاط"
        )
        s_col1, s_col2 = st.columns(2)
        with s_col1:
          team_a = st.selectbox("الفريق الأول:", family_names, key="fa")
          score_a = st.number_input("أهداف الفريق الأول:", value=0, key="sa")
        with s_col2:
          team_b = st.selectbox(
              "الفريق الثاني:",
              [f for f in family_names if f != team_a],
              key="fb",
          )
          score_b = st.number_input("أهداف الفريق الثاني:", value=0, key="sb")

        if st.button(
            f"تسجيل نتيجة {st.session_state.sport_stage} وترصيد النقاط"
        ):
          if score_a > score_b:
            st.session_state.families[team_a]["score"] += 3
            st.session_state.families[team_a]["logs"].insert(
                0,
                f"+3 نقاط (فوز في {st.session_state.sport_stage} ضد {team_b})",
            )
            save_history(
                team_a,
                3,
                f"+3 نقاط (فوز في {st.session_state.sport_stage} ضد {team_b})",
            )
            st.success(f"فاز فريق {team_a} وتم رصيد 3 نقاط بنجاح!")
          elif score_b > score_a:
            st.session_state.families[team_b]["score"] += 3
            st.session_state.families[team_b]["logs"].insert(
                0,
                f"+3 نقاط (فوز في {st.session_state.sport_stage} ضد {team_a})",
            )
            save_history(
                team_b,
                3,
                f"+3 نقاط (فوز في {st.session_state.sport_stage} ضد {team_a})",
            )
            st.success(f"فاز فريق {team_b} وتم رصيد 3 نقاط بنجاح!")
          else:
            st.session_state.families[team_a]["score"] += 1
            st.session_state.families[team_b]["score"] += 1
            st.session_state.families[team_a]["logs"].insert(
                0, f"+1 نقطة (تعادل في {st.session_state.sport_stage})"
            )
            st.session_state.families[team_b]["logs"].insert(
                0, f"+1 نقطة (تعادل في {st.session_state.sport_stage})"
            )
            save_history(
                team_a, 1, f"+1 نقطة (تعادل في {st.session_state.sport_stage})"
            )
            save_history(
                team_b, 1, f"+1 نقطة (تعادل في {st.session_state.sport_stage})"
            )
            st.success("تعادل إيجابي/سلبي، وتم رصيد نقطة لكل فريق!")
          st.rerun()

      elif st.session_state.sport_stage == "النهائي":
        st.warning(
            "🏆 مرحلة النهائي: يتم وضع الأسرتين الأكثر نقاطاً ضد بعضهما لتحديد"
            " البطل!"
        )
        sorted_fams = sorted(
            st.session_state.families.items(),
            key=lambda x: x[1]["score"],
            reverse=True,
        )
        top1 = sorted_fams[0][0]
        top2 = sorted_fams[1][0]

        st.write(
            f"طرفا المباراة النهائية بناءً على أعلى النقاط: **{top1}** ضد"
            f" **{top2}**"
        )
        champ = st.selectbox("اختر البطل الفائز بالنهائي:", [top1, top2])
        champ_pts = st.number_input("نقاط إضافية للبطل للبطولة:", value=5)

        if st.button("تتويج البطل وإغلاق الدوري"):
          st.session_state.families[champ]["score"] += champ_pts
          st.session_state.families[champ]["logs"].insert(
              0, f"+{champ_pts} نقطة (التتويج ببطولة دوري كرة القدم)"
          )
          save_history(
              champ,
              champ_pts,
              f"+{champ_pts} نقطة (التتويج ببطولة دوري كرة القدم)",
          )
          st.success(
              f"تم تتويج {champ} بطلاً لدوري كرة القدم ورصيد نقاطه بنجاح!"
          )
          st.session_state.sport_stage = "يوم الإثنين"
          save_data_to_file()
          st.rerun()

    else:
      st.subheader(
          f"🏟️ إدارة {sport_type} (مستمر لمدة ثلاثة أيام - فوز=3، تعادل=1)"
      )
      s_col1, s_col2 = st.columns(2)
      with s_col1:
        team_a = st.selectbox("الفريق الأول:", family_names, key="other_a")
        score_a = st.number_input("نقاط الفريق الأول:", value=0, key="other_sa")
      with s_col2:
        team_b = st.selectbox(
            "الفريق الثاني:",
            [f for f in family_names if f != team_a],
            key="other_b",
        )
        score_b = st.number_input("نقاط الفريق الثاني:", value=0, key="other_sb")

      if st.button("تسجيل نتيجة المباراة وترصيد النقاط"):
        if score_a > score_b:
          st.session_state.families[team_a]["score"] += 3
          st.session_state.families[team_a]["logs"].insert(
              0, f"+3 نقاط (فوز في {sport_type})"
          )
          save_history(team_a, 3, f"+3 نقاط (فوز في {sport_type})")
        elif score_b > score_a:
          st.session_state.families[team_b]["score"] += 3
          st.session_state.families[team_b]["logs"].insert(
              0, f"+3 نقاط (فوز في {sport_type})"
          )
          save_history(team_b, 3, f"+3 نقاط (فوز في {sport_type})")
        else:
          st.session_state.families[team_a]["score"] += 1
          st.session_state.families[team_b]["score"] += 1
          st.session_state.families[team_a]["logs"].insert(
              0, f"+1 نقطة (تعادل في {sport_type})"
          )
          st.session_state.families[team_b]["logs"].insert(
              0, f"+1 نقطة (تعادل في {sport_type})"
          )
          save_history(team_a, 1, f"+1 نقطة (تعادل في {sport_type})")
          save_history(team_b, 1, f"+1 نقطة (تعادل في {sport_type})")
        st.success("تم تسجيل النتيجة وحفظها بنجاح!")
        st.rerun()

    st.markdown("---")
    st.subheader("↩️ تراجع عن آخر نتيجة رياضية مسجلة")
    undo_sport_fam = st.selectbox(
        "اختر الأسرة للتراجع عن آخر نقطة أضيفت لها رياضياً:",
        family_names,
        key="undo_sport",
    )
    if st.button("تراجع عن آخر إجراء رياضي للأسرة المحددة"):
      undo_last_action(undo_sport_fam)

    st.markdown("---")
    st.subheader("🎪 المهرجان الرياضي")
    f_game = st.text_input("اسم اللعبة (مثل: ددج بول، معركة الممتلكات):")
    f_fam = st.selectbox("الأسرة:", family_names, key="f_fam")
    f_pts = st.number_input("النقاط:", value=0, key="f_pts")
    f_notes = st.text_area("ملاحظات وتقييم الأداء:")
    if st.button("اعتماد في جدول المهرجان الرياضي"):
      st.session_state.families[f_fam]["score"] += f_pts
      st.session_state.families[f_fam]["logs"].insert(
          0, f"+{f_pts} نقطة (مهرجان: {f_game or 'لعبة'})"
      )
      st.session_state.festival_logs.insert(
          0, f"🎪 {f_game} - {f_fam}: +{f_pts} نقطة. ({f_notes})"
      )
      save_history(f_fam, f_pts, f"+{f_pts} نقطة (مهرجان: {f_game or 'لعبة'})")
      st.success("تم اعتماد نتائج المهرجان الرياضي وحفظها!")
      st.rerun()

  st.markdown("---")
  st.subheader("📜 سجلات المهرجان الرياضي")
  if st.session_state.festival_logs:
    for flog in st.session_state.festival_logs:
      st.write(f"- {flog}")
  else:
    st.info("لا توجد سجلات مهرجان بعد.")

# ================= 4. البرنامج الاجتماعي =================
elif selected_section == "🤝 البرنامج الاجتماعي":
  st.header("🤝 البرنامج الاجتماعي (التقييم اليومي)")

  if is_teacher:
    st.subheader("📝 تقييم التكميل الأسري والمهام الأسرية")
    soc_fam = st.selectbox("اختر الأسرة:", family_names, key="soc_fam")
    soc_cat = st.selectbox(
        "مجال التقييم:",
        [
            (
                "التكميل الأسري (الصيحات [كلمات، إلقاء، صوت، مشاركة] - زي موحد -"
                " انضباط - تجديد وابتكار)"
            ),
            "المهام الأسرية (1. التجهيز | 2. الخدمة | 3. النظافة | 4. المساعدة)",
        ],
    )
    soc_pts = st.number_input("النقاط الممنوحة (أو الخصم):", value=0, key="soc_pts")
    soc_notes = st.text_area("ملاحظات المعلم التفصيلية:")

    if st.button("حفظ التقييم الاجتماعي"):
      st.session_state.families[soc_fam]["score"] += soc_pts
      sign = "+" if soc_pts >= 0 else ""
      st.session_state.families[soc_fam]["logs"].insert(
          0, f"{sign}{soc_pts} نقطة ({soc_cat.split()[0]})"
      )
      st.session_state.social_logs.insert(
          0,
          f"🤝 {soc_fam} [{soc_cat}]: {soc_pts} نقطة. ملاحظة: {soc_notes}",
      )
      save_history(soc_fam, soc_pts, f"{soc_pts} نقطة ({soc_cat.split()[0]})")
      st.success("تم حفظ التقييم الاجتماعي بنجاح!")
      st.rerun()

  st.markdown("---")
  st.subheader("📜 سجل الملاحظات الاجتماعية")
  if st.session_state.social_logs:
    for slog in st.session_state.social_logs:
      st.write(f"- {slog}")
  else:
    st.info("لا توجد ملاحظات اجتماعية مسجلة بعد.")
