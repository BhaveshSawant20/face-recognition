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
import mediapipe as mp

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
# FACE EMBEDDING USING MEDIA PIPE
# ===============================

mp_face = mp.solutions.face_mesh

def get_face_embedding(image_np):

    if len(image_np.shape) == 3 and image_np.shape[2] == 4:
        image_np = image_np[:, :, :3]

    image_np = image_np.astype(np.float32) / 255.0

    with mp_face.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True
    ) as face_mesh:

        results = face_mesh.process(image_np)

        if not results.multi_face_landmarks:
            return None

        embedding = []

        for lm in results.multi_face_landmarks[0].landmark:
            embedding.extend([lm.x, lm.y, lm.z])

        embedding = np.array(embedding)

        # Normalize vector
        embedding = embedding / np.linalg.norm(embedding)

        return embedding

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

        existing = supabase.table("faces_data") \
            .select("*") \
            .ilike("name", name) \
            .execute()

        if existing.data:
            st.error("User already exists")

        else:
            image = Image.open(image_buffer).convert("RGB")
            image_np = np.array(image)

            encoding = get_face_embedding(image_np)

            if encoding is None:
                st.error("No face detected")
                st.stop()

            supabase.table("faces_data").insert({
                "name": name,
                "encoding": encoding.tolist()
            }).execute()

            st.success("✅ Face registered successfully!")

# ===============================
# MARK ATTENDANCE
# ===============================

if menu == "Mark Attendance":

    st.header("🔍 Mark Attendance")

    image_buffer = st.camera_input("Capture Face")

    if image_buffer:

        image = Image.open(image_buffer).convert("RGB")
        image_np = np.array(image)

        embedding = get_face_embedding(image_np)

        if embedding is None:
            st.warning("No face detected")
            st.stop()

        faces = supabase.table("faces_data").select("*").execute()

        if not faces.data:
            st.warning("No registered faces")
            st.stop()

        best_name = None
        best_distance = float("inf")

        for face in faces.data:

            stored_embedding = np.array(face["encoding"])

            stored_embedding = stored_embedding / np.linalg.norm(stored_embedding)

            stored_embedding = np.resize(stored_embedding, len(embedding))

            dist = np.linalg.norm(embedding - stored_embedding)

            if dist < best_distance:
                best_distance = dist
                best_name = face["name"]

        st.image(image, caption="Detected Face")

        if best_distance < 0.6 and best_name:

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
                    .eq("name", best_name.lower()) \
                    .eq("lecture", current_lecture) \
                    .execute()

                if existing.data:
                    st.warning("Attendance already marked")

                else:
                    supabase.table("attendance").insert({
                        "name": best_name.lower(),
                        "lecture": current_lecture,
                        "marked_at": datetime.datetime.now().isoformat()
                    }).execute()

                    confidence = round((1 - best_distance) * 100, 2)

                    st.success(f"""
                    ✅ Attendance Marked  
                    Name: {best_name}  
                    Confidence: {confidence}%
                    """)

        else:
            st.error("Face not recognized")

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