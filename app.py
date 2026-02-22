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
import datetime
import pandas as pd
import numpy as np
from PIL import Image
from dotenv import load_dotenv
from supabase import create_client

# Recognition logic
from main import recognize_face

# ===============================
# CONFIG
# ===============================

load_dotenv()

st.set_page_config(
    page_title="AI Attendance System",
    layout="centered"
)

st.title("🎯 AI Face Attendance System")

# ===============================
# BACKGROUND
# ===============================

def set_background(image_path):

    if not os.path.exists(image_path):
        return

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/png;base64,{encoded}") no-repeat center center fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("background.png")


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

    st.header("📌 Register New Face")

    name_input = st.text_input("Enter Name")
    image_buffer = st.camera_input("Capture Face")

    if image_buffer and name_input.strip():

        name = name_input.strip().lower()

        # Duplicate check
        existing = supabase.table("faces_data") \
            .select("*") \
            .ilike("name", name) \
            .execute()

        if existing.data:
            st.error("User already exists")

        else:
            image = Image.open(image_buffer).convert("RGB")
            image_np = np.array(image)

            face_vector = np.mean(
                np.array(image.resize((32,32))),
                axis=(0,1)
            )

            supabase.table("faces_data").insert({
                "name": name,
                "encoding": face_vector.tolist()
            }).execute()

            st.success("✅ Face registered successfully!")


# ===============================
# RECOGNITION + ATTENDANCE
# ===============================

if menu == "Recognize Face":

    st.header("🔍 Face Recognition")

    image_buffer = st.camera_input("Capture Face")

    if image_buffer is not None:

        image = Image.open(image_buffer).convert("RGB")
        image_np = np.array(image)

        result = recognize_face(image_np)

        if "Welcome" in result:

            name = result.replace("Welcome", "").strip().lower()
            now = datetime.datetime.now().time()

            lecture_slots = {
                "Lecture 1": (datetime.time(9,15), datetime.time(10,15)),
                "Lecture 2": (datetime.time(10,15), datetime.time(11,15)),
                "Lecture 3": (datetime.time(11,30), datetime.time(12,30)),
                "Lecture 4": (datetime.time(12,30), datetime.time(13,30)),
                "Lecture 5": (datetime.time(14,0), datetime.time(15,0)),
                "Lecture 6": (datetime.time(15,0), datetime.time(16,0)),
            }

            current_lecture = None

            for lec,(start,end) in lecture_slots.items():
                if start <= now < end:
                    current_lecture = lec
                    break

            if not current_lecture:
                st.warning("No active lecture currently")

            else:

                existing = supabase.table("attendance") \
                    .select("*") \
                    .eq("name", name) \
                    .eq("lecture", current_lecture) \
                    .execute()

                if existing.data:
                    st.warning("Attendance already marked")

                else:
                    supabase.table("attendance").insert({
                        "name": name,
                        "lecture": current_lecture,
                        "marked_at": datetime.datetime.now().isoformat()
                    }).execute()

                    st.success(f"Attendance marked for {name}")

        else:
            st.warning(result)


# ===============================
# VIEW ATTENDANCE
# ===============================

if menu == "View Attendance":

    st.header("📊 Attendance Records")

    data = supabase.table("attendance") \
        .select("*") \
        .order("marked_at", desc=True) \
        .execute()

    if data.data:
        df = pd.DataFrame(data.data)
        st.dataframe(df, use_container_width=True)

    else:
        st.info("No records found")