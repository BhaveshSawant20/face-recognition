# import streamlit as st
# import pandas as pd
# import base64
# from main import run_attendance_frame
# from firebase_config import db
#
#
# # ---------------- PAGE ---------------- #
# st.set_page_config(
#     page_title="AI Attendance System",
#     layout="wide"
# )
#
#
# # ---------------- BACKGROUND ---------------- #
# with open("background.png", "rb") as f:
#     encoded = base64.b64encode(f.read()).decode()
#
# st.markdown(f"""
# <style>
# .stApp {{
#     background-image: url("data:image/png;base64,{encoded}");
#     background-size: cover;
#     background-position: center;
#     background-attachment: fixed;
# }}
# </style>
# """, unsafe_allow_html=True)
#
#
# st.title("🎓 AI Face Recognition Attendance")
# # st.markdown("Cloud-Based | Placement-Level Project")
#
#
# # ---------------- SESSION ---------------- #
# if "camera_running" not in st.session_state:
#     st.session_state.camera_running = False
#
# if "stop_camera" not in st.session_state:
#     st.session_state.stop_camera = False
#
#
# # ---------------- LAYOUT ---------------- #
# left, right = st.columns([1, 1.6])
#
#
# # =================================================
# # LEFT SIDE
# # =================================================
#
# with left:
#
#     st.subheader("Controls")
#
#     if st.button("🚀 Start Attendance", use_container_width=True):
#         st.session_state.camera_running = True
#         st.session_state.stop_camera = False
#         st.rerun()   # ⭐ forces layout refresh
#
#     if st.button("🛑 Stop Attendance", use_container_width=True):
#         st.session_state.stop_camera = True
#         st.session_state.camera_running = False
#         st.rerun()
#
#     st.divider()
#     st.subheader("📊 Attendance")
#
#     docs = (
#         db.collection("attendance")
#         .order_by("timestamp", direction="DESCENDING")
#         .stream()
#     )
#
#     data = [doc.to_dict() for doc in docs]
#
#     if data:
#         df = pd.DataFrame(data)
#         st.dataframe(df, use_container_width=True)
#
#         st.download_button(
#             "Download CSV",
#             df.to_csv(index=False),
#             file_name="attendance.csv",
#             use_container_width=True
#         )
#     else:
#         st.info("No attendance yet.")
#
#
#
# # =================================================
# # RIGHT SIDE (CAMERA — ALWAYS HERE)
# # =================================================
#
# with right:
#
#     st.subheader("Live Camera")
#
#     # ⭐ fixed visual container
#     camera_box = st.container()
#
#     with camera_box:
#
#         frame_placeholder = st.empty()
#
#         # ---------- PLACEHOLDER IMAGE ----------
#         if not st.session_state.camera_running:
#
#             frame_placeholder.image(
#                 "placeholder.png",  # put this file in root
#                 use_container_width=True
#             )
#
#         else:
#
#             run_attendance_frame(frame_placeholder)

import streamlit as st
import base64
import os

# -------- Function to Set Background -------- #
def set_background(image_path):

    if not os.path.exists(image_path):
        st.error("Background image not found. Check file path.")
        return

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    page_bg = f"""
    <style>
    .stApp {{
        background: url("data:image/png;base64,{encoded_string}") no-repeat center center fixed;
        background-size: cover;
    }}

    /* Dark overlay for readability */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.55);
        backdrop-filter: blur(4px);
        z-index: -1;
    }}

    /* Make main container slightly transparent */
    .block-container {{
        background: rgba(255, 255, 255, 0.08);
        padding: 2rem;
        border-radius: 15px;
    }}
    </style>
    """

    st.markdown(page_bg, unsafe_allow_html=True)


# -------- Call the Function -------- #
set_background("background.png")


from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import face_recognition
import numpy as np
from PIL import Image
from supabase import create_client
import os
import datetime
import pandas as pd
from main import recognize_face

# =========================
# SUPABASE CONNECTION
# =========================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase environment variables not set.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(page_title="AI Attendance System", layout="centered")
st.title("🎯 AI Face Recognition Attendance System")

menu = st.sidebar.selectbox(
    "Choose Mode",
    ["Register Face", "Recognize Face", "View Attendance"]
)

# =========================
# REGISTER FACE
# =========================

if menu == "Register Face":

    st.header("📌 Register New Face")

    name_input = st.text_input("Enter Name")
    image_buffer = st.camera_input("Capture Face")

    if image_buffer is not None and name_input.strip() != "":

        name = name_input.strip().lower()

        # Case-insensitive duplicate check
        existing_user = supabase.table("faces_data") \
            .select("*") \
            .ilike("name", name) \
            .execute()

        if existing_user.data:
            st.error("This name is already registered.")
        else:
            image = Image.open(image_buffer)
            image_np = np.array(image)

            face_locations = face_recognition.face_locations(image_np)
            face_encodings = face_recognition.face_encodings(image_np, face_locations)

            if not face_encodings:
                st.error("No face detected. Try again.")
            elif len(face_encodings) > 1:
                st.error("Multiple faces detected. Capture only one face.")
            else:
                encoding = face_encodings[0]

                supabase.table("faces_data").insert({
                    "name": name,
                    "encoding": encoding.tolist()
                }).execute()

                st.success(f"✅ {name.capitalize()} registered successfully!")

# =========================
# RECOGNIZE FACE
# =========================

if menu == "Recognize Face":

    st.header("🔍 Face Recognition")

    image_buffer = st.camera_input("Capture Face")

    if image_buffer is not None:

        image = Image.open(image_buffer)
        image_np = np.array(image)

        result = recognize_face(image_np)

        if "Welcome" in result:

            name = result.replace("Welcome ", "").strip().lower()
            now = datetime.datetime.now().time()

            # ===== YOUR EXACT LECTURE TIMINGS =====
            lecture_slots = {
                "Lecture 1": (datetime.time(9, 15), datetime.time(10, 15)),
                "Lecture 2": (datetime.time(10, 15), datetime.time(11, 15)),
                "Lecture 3": (datetime.time(11, 30), datetime.time(12, 30)),
                "Lecture 4": (datetime.time(12, 30), datetime.time(13, 30)),
                "Lecture 5": (datetime.time(14, 0), datetime.time(15, 0)),
                "Lecture 6": (datetime.time(15, 0), datetime.time(16, 0)),
            }

            current_lecture = None

            for lecture, (start, end) in lecture_slots.items():
                if start <= now < end:   # No overlap bug
                    current_lecture = lecture
                    break

            if not current_lecture:
                st.warning("⚠ No active lecture at this time.")
            else:
                # Check duplicate for same lecture
                existing_attendance = supabase.table("attendance") \
                    .select("*") \
                    .eq("name", name) \
                    .eq("lecture", current_lecture) \
                    .execute()

                if existing_attendance.data:
                    st.warning(
                        f"⚠ {name.capitalize()} has already marked attendance for {current_lecture}."
                    )
                else:
                    supabase.table("attendance").insert({
                        "name": name,
                        "lecture": current_lecture,
                        "marked_at": datetime.datetime.now().isoformat()
                    }).execute()

                    st.success(
                        f"✅ Attendance marked for {name.capitalize()} - {current_lecture}"
                    )

        elif "detected" in result:
            st.error(result)
        else:
            st.warning(result)

# =========================
# VIEW ATTENDANCE
# =========================

if menu == "View Attendance":

    st.header("📊 Attendance Records")

    response = supabase.table("attendance") \
        .select("*") \
        .order("marked_at", desc=True) \
        .execute()

    attendance_data = response.data

    if attendance_data:
        df = pd.DataFrame(attendance_data)
        df["name"] = df["name"].str.capitalize()
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No attendance records found.")