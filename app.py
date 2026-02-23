# import streamlit as st
# import os
# import datetime
# import pandas as pd
# from PIL import Image
# from dotenv import load_dotenv
# from supabase import create_client
# import tempfile
# import pytz
#
# # DeepFace logic
# from main import identify_person
#
# # ===============================
# # CONFIG
# # ===============================
#
# load_dotenv()
#
# st.set_page_config(
#     page_title="AI Attendance System",
#     layout="centered"
# )
#
# st.title("🎯 AI Face Attendance System")
#
# # ===============================
# # SUPABASE CONNECTION
# # ===============================
#
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
#
# if not SUPABASE_URL or not SUPABASE_KEY:
#     st.error("Supabase environment variables missing")
#     st.stop()
#
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
#
# # ===============================
# # SIDEBAR MENU
# # ===============================
#
# menu = st.sidebar.selectbox(
#     "Choose Mode",
#     ["Register Face", "Mark Attendance", "View Attendance"]
# )
#
# # ===============================
# # REGISTER STUDENT
# # ===============================
#
# if menu == "Register Face":
#
#     st.header("📌 Register New Student")
#
#     name_input = st.text_input("Enter Student Name")
#
#     image_buffer = st.camera_input("Capture Face", key="register_camera")
#
#     # Centered Button
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         register_clicked = st.button("Register Student", use_container_width=True)
#
#     if register_clicked:
#
#         if not name_input.strip():
#             st.warning("Enter student name first")
#         elif not image_buffer:
#             st.warning("Capture image first")
#         else:
#             name = name_input.strip().lower()
#
#             existing = supabase.table("faces_data") \
#                 .select("*") \
#                 .ilike("name", name) \
#                 .execute()
#
#             if existing.data:
#                 st.error("Student already exists")
#             else:
#                 try:
#                     with st.spinner("Registering student..."):
#
#                         image = Image.open(image_buffer).convert("RGB")
#
#                         with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
#                             image.save(tmp.name)
#
#                             with open(tmp.name, "rb") as f:
#                                 supabase.storage.from_("faces").upload(
#                                     f"{name}.png",
#                                     f,
#                                     {
#                                         "content-type": "image/png",
#                                         "upsert": "true"
#                                     }
#                                 )
#
#                         supabase.table("faces_data").insert({
#                             "name": name
#                         }).execute()
#
#                     st.success("✅ Student registered successfully!")
#
#                 except Exception as e:
#                     st.error(f"Upload failed: {str(e)}")
#
#
# # ===============================
# # MARK ATTENDANCE
# # ===============================
#
# if menu == "Mark Attendance":
#
#     st.header("📝 Mark Attendance")
#
#     image_buffer = st.camera_input("Capture Face", key="attendance_camera")
#
#     # Centered Button
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         mark_clicked = st.button("Mark Attendance", use_container_width=True)
#
#     if mark_clicked:
#
#         if not image_buffer:
#             st.warning("Capture image first")
#         else:
#             try:
#                 with st.spinner("Recognizing student..."):
#
#                     image = Image.open(image_buffer).convert("RGB")
#
#                     with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
#                         image.save(tmp.name)
#                         temp_path = tmp.name
#
#                     name, message = identify_person(temp_path)
#
#                 if name:
#
#                     ist = pytz.timezone("Asia/Kolkata")
#                     now = datetime.datetime.now(ist)
#                     current_time = now.time()
#
#                     lecture_slots = {
#                         "Lecture 1": (datetime.time(9, 15), datetime.time(10, 15)),
#                         "Lecture 2": (datetime.time(10, 15), datetime.time(11, 15)),
#                         "Lecture 3": (datetime.time(11, 30), datetime.time(12, 30)),
#                         "Lecture 4": (datetime.time(12, 30), datetime.time(13, 30)),
#                         "Lecture 5": (datetime.time(14, 0), datetime.time(15, 0)),
#                         "Lecture 6": (datetime.time(15, 0), datetime.time(16, 0)),
#                     }
#
#                     current_lecture = None
#
#                     for lec, (start, end) in lecture_slots.items():
#                         if start <= current_time < end:
#                             current_lecture = lec
#                             break
#
#                     if not current_lecture:
#                         st.warning("No active lecture currently")
#                     else:
#                         existing = supabase.table("attendance") \
#                             .select("*") \
#                             .eq("name", name) \
#                             .eq("lecture", current_lecture) \
#                             .execute()
#
#                         if existing.data:
#                             st.warning("⚠ Attendance already marked")
#                         else:
#                             supabase.table("attendance").insert({
#                                 "name": name,
#                                 "lecture": current_lecture,
#                                 "marked_at": now.isoformat()
#                             }).execute()
#
#                             st.success(f"✅ Attendance marked for {name}")
#
#                 else:
#                     st.warning(message)
#
#             except Exception as e:
#                 st.error(f"Recognition failed: {str(e)}")
#
# # ===============================
# # VIEW ATTENDANCE
# # ===============================
#
# if menu == "View Attendance":
#
#     st.header("📊 Attendance Records")
#
#     data = supabase.table("attendance") \
#         .select("*") \
#         .order("marked_at", desc=True) \
#         .execute()
#
#     if data.data:
#         df = pd.DataFrame(data.data)
#         st.dataframe(df, use_container_width=True)
#     else:
#         st.info("No records found")

import streamlit as st
import os
import datetime
import pandas as pd
from PIL import Image
from dotenv import load_dotenv
from supabase import create_client
import tempfile
import pytz
from dateutil import parser
import base64

from main import identify_person

# ===============================
# CONFIG
# ===============================
load_dotenv()
st.set_page_config(page_title="AI Attendance System", layout="centered")

# ===============================
# BACKGROUND + GLASS EFFECT (LIGHT THEME)
# ===============================
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        /* Main Background */
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Sidebar Background */
        section[data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}

        /* GLASS CONTAINER - Light */
        .block-container {{
            background: rgba(255, 255, 255, 0.65);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border-radius: 25px;
            border: 1px solid rgba(0, 0, 0, 0.1);
            padding: 2.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        }}

        /* All text black */
        h1, h2, h3, h4, h5, h6, p, label, div, span {{
            color: black !important;
        }}

        /* Sidebar text black */
        section[data-testid="stSidebar"] * {{
            color: black !important;
        }}

        /* Buttons Styling */
        .stButton>button {{
            border-radius: 12px;
            border: 1px solid rgba(0,0,0,0.2);
            background: rgba(255,255,255,0.8);
            color: black;
            font-weight: bold;
        }}

        .stButton>button:hover {{
            background: rgba(255,255,255,1);
        }}

        /* Radio buttons & inputs */
        .stRadio label {{
            color: black !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local("background.png")

st.title("🎯 AI Face Attendance System")

# ===============================
# SUPABASE CONNECTION
# ===============================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase environment variables missing")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===============================
# SIDEBAR MENU
# ===============================
menu = st.sidebar.selectbox(
    "Choose Mode",
    ["Register Face", "Mark Attendance", "View Attendance"]
)

# ===============================
# REGISTER FACE
# ===============================
if menu == "Register Face":
    st.header("📌 Register New Student")

    full_name = st.text_input("Enter Full Name")
    roll_no_input = st.text_input("Enter Roll No")
    image_buffer = st.camera_input("Capture Face", key="register_camera")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        register_clicked = st.button("Register Student", use_container_width=True)

    if register_clicked:
        if not full_name.strip():
            st.warning("Enter student full name")
        elif not roll_no_input.strip():
            st.warning("Enter roll number")
        elif not image_buffer:
            st.warning("Capture image first")
        else:
            name = full_name.strip()
            roll_no = roll_no_input.strip()

            try:
                existing_roll = supabase.table("faces_data").select("*").eq("roll_no", roll_no).execute()
                if existing_roll.data:
                    st.error("Roll number already exists")
                    st.stop()

                with st.spinner("Registering student..."):
                    image = Image.open(image_buffer).convert("RGB")
                    filename = f"{roll_no}_{name}.png"

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        image.save(tmp.name)
                        with open(tmp.name, "rb") as f:
                            supabase.storage.from_("faces").upload(
                                filename,
                                f,
                                {"content-type": "image/png", "upsert": "true"}
                            )

                    supabase.table("faces_data").insert({
                        "name": name,
                        "roll_no": roll_no,
                        "image_path": filename
                    }).execute()

                st.success(f"✅ Student {name} registered successfully!")

            except Exception as e:
                st.error(f"Registration failed: {str(e)}")

# ===============================
# MARK ATTENDANCE
# ===============================
if menu == "Mark Attendance":
    st.header("📝 Mark Attendance")

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist)

    st.write(f"📅 Date: {now.strftime('%d-%m-%Y')}")
    st.write(f"⏰ Time: {now.strftime('%H:%M:%S')}")

    image_buffer = st.camera_input("Capture Face", key="attendance_camera")
    st.markdown("---")

    roll_no_input = st.text_input("Enter Roll No")

    st.markdown("### Select Lecture")
    subjects = ["SPCC", "CSS", "MC", "AI", "IOT", "CC", "MINI PROJECT"]
    subject = st.radio("Select Lecture", options=subjects, horizontal=True)

    st.markdown("---")

    colA, colB, colC = st.columns([1, 2, 1])
    with colB:
        mark_clicked = st.button("Mark Attendance", use_container_width=True)

    if mark_clicked:
        if not image_buffer:
            st.warning("Capture image first")
        elif not roll_no_input.strip():
            st.warning("Enter roll number")
        else:
            try:
                image = Image.open(image_buffer).convert("RGB")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    image.save(tmp.name)
                    temp_path = tmp.name

                recognized_name, recognized_roll, message = identify_person(temp_path)

                if not recognized_name:
                    st.warning(message)
                    st.stop()

                roll_no = roll_no_input.strip()

                registered = supabase.table("faces_data").select("*").eq("roll_no", roll_no).execute()
                if not registered.data:
                    st.error("❌ Roll number not registered")
                    st.stop()

                registered_name = registered.data[0]["name"]

                if recognized_name.lower() != registered_name.lower() or recognized_roll != roll_no:
                    st.error("❌ Face does not match the registered roll number")
                    st.stop()

                COOLDOWN_MINUTES = 45
                last_record = supabase.table("attendance") \
                    .select("marked_at") \
                    .eq("roll_no", roll_no) \
                    .order("marked_at", desc=True) \
                    .limit(1) \
                    .execute()

                if last_record.data:
                    last_time = parser.isoparse(last_record.data[0]["marked_at"])
                    if last_time.tzinfo is None:
                        last_time = ist.localize(last_time)
                    diff_minutes = (now - last_time).total_seconds() / 60
                    if diff_minutes < COOLDOWN_MINUTES:
                        remaining = int(COOLDOWN_MINUTES - diff_minutes)
                        st.error(f"⛔ Cooldown active. Try again after {remaining} minutes.")
                        st.stop()

                existing_attendance = supabase.table("attendance") \
                    .select("*") \
                    .eq("roll_no", roll_no) \
                    .eq("subject", subject) \
                    .eq("date", now.date().isoformat()) \
                    .execute()

                if existing_attendance.data:
                    st.warning("⚠ Attendance already marked for this lecture today")
                    st.stop()

                supabase.table("attendance").insert({
                    "roll_no": roll_no,
                    "name": recognized_name,
                    "subject": subject,
                    "date": now.date().isoformat(),
                    "time": now.strftime("%H:%M:%S"),
                    "marked_at": now.isoformat()
                }).execute()

                st.success(f"✅ Attendance marked for {recognized_name} ({subject})")

            except Exception as e:
                st.error(f"Recognition failed: {str(e)}")

# ===============================
# VIEW ATTENDANCE
# ===============================
if menu == "View Attendance":
    st.header("📊 Attendance Records")

    data = supabase.table("attendance").select("*").order("marked_at", desc=True).execute()

    if data.data:
        df = pd.DataFrame(data.data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records found")