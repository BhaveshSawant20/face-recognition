# import streamlit as st
# import os
# import datetime
# import pandas as pd
# from PIL import Image
# from dotenv import load_dotenv
# from supabase import create_client
# import tempfile
# import pytz
# import base64
#
# from main import identify_person
#
# # ===============================
# # CONFIG
# # ===============================
# load_dotenv()
# st.set_page_config(page_title="AI Attendance System", layout="centered")
#
# # ===============================
# # BACKGROUND + GLASS STYLE
# # ===============================
# def add_bg_from_local(image_file):
#     with open(image_file, "rb") as f:
#         encoded_string = base64.b64encode(f.read()).decode()
#
#     st.markdown(
#         f"""
#         <style>
#
#         .stApp {{
#             background-image: url("data:image/png;base64,{encoded_string}");
#             background-size: cover;
#             background-position: center;
#             background-repeat: no-repeat;
#             background-attachment: fixed;
#         }}
#
#         section[data-testid="stSidebar"] {{
#             background-image: url("data:image/png;base64,{encoded_string}");
#             background-size: cover;
#         }}
#
#         /* MAIN GLASS CONTAINER */
#         .block-container {{
#             background: rgba(255, 255, 255, 0.25);
#             backdrop-filter: blur(20px);
#             -webkit-backdrop-filter: blur(20px);
#             border-radius: 25px;
#             border: 1px solid rgba(255,255,255,0.4);
#             padding: 2.5rem;
#             box-shadow: 0 8px 32px rgba(0,0,0,0.2);
#             color: black !important;
#         }}
#
#         /* Force BLACK text inside main container */
#         .block-container h1,
#         .block-container h2,
#         .block-container h3,
#         .block-container h4,
#         .block-container p,
#         .block-container label,
#         .block-container span,
#         .block-container div {{
#             color: black !important;
#         }}
#
#         /* INPUT BOX STYLE */
#         input, textarea {{
#             background-color: rgba(0,0,0,0.85) !important;
#             color: white !important;
#             border-radius: 10px !important;
#             border: 1px solid rgba(255,255,255,0.4) !important;
#         }}
#
#         /* CAMERA BUTTON FIX (Take Photo / Clear Photo) */
#         button[kind="secondary"] {{
#             color: white !important;
#         }}
#
#         div[data-testid="stCameraInput"] button {{
#             color: white !important;
#         }}
#
#         div[data-testid="stCameraInput"] {{
#             color: white !important;
#         }}
#
#         /* CENTER MAIN BUTTONS */
#         div[data-testid="stButton"] {{
#             display: flex;
#             justify-content: center;
#         }}
#
#         div[data-testid="stButton"] > button {{
#             border-radius: 12px;
#             border: 1px solid rgba(0,0,0,0.3);
#             background: rgba(255,255,255,0.6);
#             backdrop-filter: blur(10px);
#             color: black !important;
#             font-weight: bold;
#             padding: 10px 30px;
#         }}
#
#         div[data-testid="stButton"] > button:hover {{
#             background: rgba(255,255,255,0.85);
#         }}
#
#         /* GLASS TABLE */
#         .stDataFrame {{
#             background: rgba(255,255,255,0.35) !important;
#             backdrop-filter: blur(10px);
#             border-radius: 15px;
#             padding: 10px;
#             color: black !important;
#         }}
#
#         </style>
#         """,
#         unsafe_allow_html=True
#     )
#
# add_bg_from_local("background.jpg")
#
# st.title("🎯 AI Face Attendance System")
#
# # ===============================
# # SUPABASE
# # ===============================
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
# # SIDEBAR
# # ===============================
# menu = st.sidebar.selectbox(
#     "Choose Mode",
#     ["Register Face", "Mark Attendance", "View Attendance"]
# )
#
# # ===============================
# # REGISTER
# # ===============================
# if menu == "Register Face":
#     st.header("📌 Register New Student")
#
#     full_name = st.text_input("Enter Full Name")
#     roll_no_input = st.text_input("Enter Roll No")
#     image_buffer = st.camera_input("Capture Face")
#
#     col1, col2, col3 = st.columns([1, 2, 1])
#
#     with col2:
#         register_clicked = st.button("Register Student", use_container_width=True)
#
#     if register_clicked:
#         if not full_name or not roll_no_input or not image_buffer:
#             st.warning("Fill all fields and capture image")
#         else:
#             name = full_name.strip()
#             roll_no = roll_no_input.strip()
#
#             existing = supabase.table("faces_data").select("*").eq("roll_no", roll_no).execute()
#
#             if existing.data:
#                 existing_name = existing.data[0]["name"]
#                 st.error(f"❌ Student '{existing_name}' is already registered with Roll No {roll_no}")
#             else:
#                 image = Image.open(image_buffer).convert("RGB")
#                 filename = f"{roll_no}_{name}.png"
#
#                 with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
#                     image.save(tmp.name)
#                     with open(tmp.name, "rb") as f:
#                         supabase.storage.from_("faces").upload(
#                             filename, f,
#                             {"content-type": "image/png", "upsert": "true"}
#                         )
#
#                 supabase.table("faces_data").insert({
#                     "name": name,
#                     "roll_no": roll_no,
#                     "image_path": filename
#                 }).execute()
#
#                 st.success("Student Registered Successfully ✅")
#
# # ===============================
# # MARK ATTENDANCE
# # ===============================
# if menu == "Mark Attendance":
#     st.header("📝 Mark Attendance")
#
#     ist = pytz.timezone("Asia/Kolkata")
#     now = datetime.datetime.now(ist)
#
#     st.write(f"📅 {now.strftime('%d-%m-%Y')}  ⏰ {now.strftime('%H:%M:%S')}")
#
#     image_buffer = st.camera_input("Capture Face")
#     roll_no_input = st.text_input("Enter Roll No")
#
#     subjects = ["SPCC", "CSS", "MC", "AI", "IOT", "CC", "MINI PROJECT"]
#     subject = st.radio("Select Lecture", subjects, horizontal=True)
#
#     col1, col2, col3 = st.columns([1, 2, 1])
#
#     with col2:
#         mark_clicked = st.button("Mark Attendance", use_container_width=True)
#
#     if mark_clicked:
#         if not image_buffer or not roll_no_input:
#             st.warning("Capture image and enter roll number")
#         else:
#             image = Image.open(image_buffer).convert("RGB")
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
#                 image.save(tmp.name)
#                 temp_path = tmp.name
#
#             recognized_name, recognized_roll, message = identify_person(temp_path)
#
#             if not recognized_name:
#                 st.error(message)
#             else:
#                 supabase.table("attendance").insert({
#                     "roll_no": roll_no_input,
#                     "name": recognized_name,
#                     "subject": subject,
#                     "date": now.date().isoformat(),
#                     "time": now.strftime("%H:%M:%S"),
#                     "marked_at": now.isoformat()
#                 }).execute()
#
#                 st.success("Attendance Marked Successfully ✅")
#
# # ===============================
# # VIEW ATTENDANCE
# # ===============================
# if menu == "View Attendance":
#     st.header("📊 Attendance Dashboard")
#
#     data = supabase.table("attendance").select("*").order("marked_at", desc=True).execute()
#
#     if data.data:
#         df = pd.DataFrame(data.data)
#
#         st.subheader("📋 Attendance Records")
#         st.dataframe(df, use_container_width=True)
#
#         st.subheader("📊 Attendance Analytics")
#         subject_count = df["subject"].value_counts()
#         st.bar_chart(subject_count)
#
#     else:
#         st.info("No attendance records found")
#


import streamlit as st
import os
import datetime
import pandas as pd
from PIL import Image
from dotenv import load_dotenv
from supabase import create_client
import tempfile
import pytz
import base64

from main import identify_person

# ===============================
# CONFIG
# ===============================
load_dotenv()
st.set_page_config(page_title="AI Attendance System", layout="centered")

# ===============================
# BACKGROUND + GLASS STYLE
# ===============================
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <style>

        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        section[data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
        }}

        .block-container {{
            background: rgba(255,255,255,0.25);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            border: 1px solid rgba(255,255,255,0.4);
            padding: 2.5rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            color: black !important;
        }}

        .block-container h1, .block-container h2,
        .block-container h3, .block-container h4,
        .block-container p, .block-container label,
        .block-container span, .block-container div {{
            color: black !important;
        }}

        input, textarea {{
            background-color: rgba(0,0,0,0.85) !important;
            color: white !important;
            border-radius: 10px !important;
        }}

        button[kind="secondary"],
        div[data-testid="stCameraInput"] *,
        div[data-testid="stCameraInput"] button,
        div[data-testid="stCameraInput"] button span {{
            color: white !important;
        }}

        div[data-testid="stButton"] {{
            text-align: center !important;
        }}

        div[data-testid="stButton"] > button {{
            display: inline-block !important;
            margin: 0 auto !important;
            width: 60%;
            background-color: white !important;
            color: black !important;
            border-radius: 12px !important;
            border: 1px solid rgba(0,0,0,0.3) !important;
            font-weight: bold !important;
            padding: 10px 20px !important;
        }}

        div[data-testid="stButton"] > button:hover {{
            background-color: white !important;
            color: black !important;
        }}

        </style>
    """, unsafe_allow_html=True)

add_bg_from_local("background.jpg")

st.title("🎯 AI Face Attendance System")

# ===============================
# SUPABASE
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
    image_buffer = st.camera_input("Capture Face")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        register_clicked = st.button("Register Student", use_container_width=True)

    if register_clicked:
        if not full_name or not roll_no_input or not image_buffer:
            st.warning("Fill all fields and capture image")
        else:
            name = full_name.strip()
            roll_no = roll_no_input.strip()

            existing = supabase.table("faces_data") \
                .select("*") \
                .eq("roll_no", roll_no) \
                .execute()

            if existing.data:
                existing_name = existing.data[0]["name"]
                st.error(f"❌ Student '{existing_name}' is already registered.")
            else:
                image = Image.open(image_buffer).convert("RGB")
                filename = f"{roll_no}_{name}.png"

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    image.save(tmp.name)
                    with open(tmp.name, "rb") as f:
                        supabase.storage.from_("faces").upload(
                            filename, f,
                            {"content-type": "image/png", "upsert": "true"}
                        )

                supabase.table("faces_data").insert({
                    "name": name,
                    "roll_no": roll_no,
                    "image_path": filename
                }).execute()

                st.success(f"✅ Student {name} registered successfully!")

# ===============================
# MARK ATTENDANCE
# ===============================
if menu == "Mark Attendance":
    st.header("📝 Mark Attendance")

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist)

    st.write(f"📅 {now.strftime('%d-%m-%Y')}  ⏰ {now.strftime('%H:%M:%S')}")

    image_buffer = st.camera_input("Capture Face")
    roll_no_input = st.text_input("Enter Roll No")

    subjects = ["SPCC", "CSS", "MC", "AI", "IOT", "CC", "MINI PROJECT"]
    subject = st.radio("Select Lecture", subjects, horizontal=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mark_clicked = st.button("Mark Attendance", use_container_width=True)

    if mark_clicked:
        if not image_buffer or not roll_no_input:
            st.warning("Capture image and enter roll number")
        else:
            image = Image.open(image_buffer).convert("RGB")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                image.save(tmp.name)
                temp_path = tmp.name

            recognized_name, recognized_roll, message = identify_person(temp_path)

            if not recognized_name:
                st.error(message)

            elif recognized_roll != roll_no_input.strip():
                st.error("Roll number does not match recognized face ❌")

            else:
                last_record = supabase.table("attendance") \
                    .select("*") \
                    .eq("roll_no", recognized_roll) \
                    .order("marked_at", desc=True) \
                    .limit(1) \
                    .execute()

                if last_record.data:
                    last_time = datetime.datetime.fromisoformat(
                        last_record.data[0]["marked_at"]
                    )

                    time_difference = (now - last_time).total_seconds() / 60

                    if time_difference < 45:
                        remaining = 45 - int(time_difference)
                        st.error(
                            f"⏳ You must wait {remaining} more minutes before marking attendance again."
                        )
                        st.stop()

                supabase.table("attendance").insert({
                    "roll_no": recognized_roll,
                    "name": recognized_name,
                    "subject": subject,
                    "date": now.date().isoformat(),
                    "time": now.strftime("%H:%M:%S"),
                    "marked_at": now.isoformat()
                }).execute()

                st.success(f"✅ Attendance marked for {recognized_name} ({subject})")

# ===============================
# VIEW ATTENDANCE
# ===============================
if menu == "View Attendance":
    st.header("📊 Attendance Dashboard")

    data = supabase.table("attendance") \
        .select("*") \
        .order("marked_at", desc=True) \
        .execute()

    if data.data:
        df = pd.DataFrame(data.data)

        st.subheader("📋 Attendance Records")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Subject Wise Attendance")
        subject_count = df["subject"].value_counts()
        st.bar_chart(subject_count)
    else:
        st.info("No attendance records found")