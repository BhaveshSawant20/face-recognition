import streamlit as st
import pandas as pd
import base64
from main import run_attendance_frame
from firebase_config import db


# ---------------- PAGE ---------------- #
st.set_page_config(
    page_title="AI Attendance System",
    layout="wide"
)


# ---------------- BACKGROUND ---------------- #
with open("background.png", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/png;base64,{encoded}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
</style>
""", unsafe_allow_html=True)


st.title("🎓 AI Face Recognition Attendance")
# st.markdown("Cloud-Based | Placement-Level Project")


# ---------------- SESSION ---------------- #
if "camera_running" not in st.session_state:
    st.session_state.camera_running = False

if "stop_camera" not in st.session_state:
    st.session_state.stop_camera = False


# ---------------- LAYOUT ---------------- #
left, right = st.columns([1, 1.6])


# =================================================
# LEFT SIDE
# =================================================

with left:

    st.subheader("Controls")

    if st.button("🚀 Start Attendance", use_container_width=True):
        st.session_state.camera_running = True
        st.session_state.stop_camera = False
        st.rerun()   # ⭐ forces layout refresh

    if st.button("🛑 Stop Attendance", use_container_width=True):
        st.session_state.stop_camera = True
        st.session_state.camera_running = False
        st.rerun()

    st.divider()
    st.subheader("📊 Attendance")

    docs = (
        db.collection("attendance")
        .order_by("timestamp", direction="DESCENDING")
        .stream()
    )

    data = [doc.to_dict() for doc in docs]

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            file_name="attendance.csv",
            use_container_width=True
        )
    else:
        st.info("No attendance yet.")



# =================================================
# RIGHT SIDE (CAMERA — ALWAYS HERE)
# =================================================

with right:

    st.subheader("Live Camera")

    # ⭐ fixed visual container
    camera_box = st.container()

    with camera_box:

        frame_placeholder = st.empty()

        # ---------- PLACEHOLDER IMAGE ----------
        if not st.session_state.camera_running:

            frame_placeholder.image(
                "placeholder.png",  # put this file in root
                use_container_width=True
            )

        else:

            run_attendance_frame(frame_placeholder)
