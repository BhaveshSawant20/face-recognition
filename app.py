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
#     st.markdown(f"""
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
#         .block-container {{
#             background: rgba(255,255,255,0.25);
#             backdrop-filter: blur(20px);
#             border-radius: 25px;
#             border: 1px solid rgba(255,255,255,0.4);
#             padding: 2.5rem;
#             box-shadow: 0 8px 32px rgba(0,0,0,0.2);
#             color: black !important;
#         }}
#
#         .block-container h1, .block-container h2,
#         .block-container h3, .block-container h4,
#         .block-container p, .block-container label,
#         .block-container span, .block-container div {{
#             color: black !important;
#         }}
#
#         input, textarea {{
#             background-color: rgba(0,0,0,0.85) !important;
#             color: white !important;
#             border-radius: 10px !important;
#         }}
#
#         button[kind="secondary"],
#         div[data-testid="stCameraInput"] *,
#         div[data-testid="stCameraInput"] button,
#         div[data-testid="stCameraInput"] button span {{
#             color: white !important;
#         }}
#
#         div[data-testid="stButton"] {{
#             text-align: center !important;
#         }}
#
#         div[data-testid="stButton"] > button {{
#             display: inline-block !important;
#             margin: 0 auto !important;
#             width: 60%;
#             background-color: white !important;
#             color: black !important;
#             border-radius: 12px !important;
#             border: 1px solid rgba(0,0,0,0.3) !important;
#             font-weight: bold !important;
#             padding: 10px 20px !important;
#             transition: all 0.2s ease-in-out;
#         }}
#
#         div[data-testid="stButton"] > button:hover {{
#             background-color: #4CAF50 !important;
#             color: white !important;
#             box-shadow: 0 6px 10px rgba(0,0,0,0.15);
#             transform: translateY(-2px);
#         }}
#
#         div[data-testid="stButton"] > button:active {{
#             background-color: #45a049 !important;
#             transform: translateY(1px);
#             box-shadow: 0 2px 4px rgba(0,0,0,0.2);
#         }}
#
#         </style>
#     """, unsafe_allow_html=True)
#
# add_bg_from_local("background.jpg")
#
# st.title(" AI Face Attendance System")
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
# # SIDEBAR MENU
# # ===============================
# menu = st.sidebar.selectbox(
#     "Choose Mode",
#     ["Register Face", "Mark Attendance", "View Attendance"]
# )
#
# # ===============================
# # REGISTER FACE
# # ===============================
# if menu == "Register Face":
#     st.header("📌 Register New Student")
#
#     full_name = st.text_input("Enter Full Name")
#     roll_no_input = st.text_input("Enter Roll No")
#     image_buffer = st.camera_input("Capture Face")
#
#     col1, col2, col3 = st.columns([1, 2, 1])
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
#             existing = supabase.table("faces_data") \
#                 .select("*") \
#                 .eq("roll_no", roll_no) \
#                 .execute()
#
#             if existing.data:
#                 existing_name = existing.data[0]["name"]
#                 st.error(f"❌ Student '{existing_name}' is already registered.")
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
#                 st.success(f"✅ Student {name} registered successfully!")
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
#
#             elif recognized_roll != roll_no_input.strip():
#                 st.error("Roll number does not match recognized face ❌")
#
#             else:
#                 last_record = supabase.table("attendance") \
#                     .select("*") \
#                     .eq("roll_no", recognized_roll) \
#                     .order("marked_at", desc=True) \
#                     .limit(1) \
#                     .execute()
#
#                 if last_record.data:
#                     last_time = datetime.datetime.fromisoformat(
#                         last_record.data[0]["marked_at"]
#                     )
#
#                     time_difference = (now - last_time).total_seconds() / 60
#
#                     if time_difference < 45:
#                         remaining = 45 - int(time_difference)
#                         st.error(
#                             f"⏳ You must wait {remaining} more minutes before marking attendance again."
#                         )
#                         st.stop()
#
#                 supabase.table("attendance").insert({
#                     "roll_no": recognized_roll,
#                     "name": recognized_name,
#                     "subject": subject,
#                     "date": now.date().isoformat(),
#                     "time": now.strftime("%H:%M:%S"),
#                     "marked_at": now.isoformat()
#                 }).execute()
#
#                 st.success(f"✅ Attendance marked for {recognized_name} ({subject})")
#
# # ===============================
# # VIEW ATTENDANCE
# # ===============================
# if menu == "View Attendance":
#     st.header("📊 Attendance Dashboard")
#
#     data = supabase.table("attendance") \
#         .select("*") \
#         .order("marked_at", desc=True) \
#         .execute()
#
#     if data.data:
#         df = pd.DataFrame(data.data)
#
#         st.subheader("📋 Attendance Records")
#         st.dataframe(df, use_container_width=True)
#
#         st.subheader("📊 Subject Wise Attendance")
#         subject_count = df["subject"].value_counts()
#         st.bar_chart(subject_count)
#     else:
#         st.info("No attendance records found")
#
#


import streamlit as st
import streamlit.components.v1 as components
import os
import datetime
import pandas as pd
from PIL import Image
from dotenv import load_dotenv
from supabase import create_client
import tempfile
import pytz
import base64
import math
from streamlit_geolocation import streamlit_geolocation

from main import identify_person

# ===============================
# CONFIG
# ===============================

load_dotenv()
st.set_page_config(page_title="AI Attendance System", layout="centered")

# ===============================
# COLLEGE LOCATION CONFIG
# ===============================

COLLEGE_LAT = 19.26632227483217
COLLEGE_LON = 72.97470227315154
ALLOWED_RADIUS_METERS = 200


def is_within_radius(user_lat, user_lon, college_lat, college_lon, radius_m):
    R = 6371000

    phi1 = math.radians(user_lat)
    phi2 = math.radians(college_lat)

    delta_phi = math.radians(college_lat - user_lat)
    delta_lambda = math.radians(college_lon - user_lon)

    a = (
        math.sin(delta_phi / 2) ** 2 +
        math.cos(phi1) * math.cos(phi2) *
        math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance <= radius_m, distance


# ===============================
# BACKGROUND + GLASS STYLE + GREEN HOVER BUTTONS
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

        /* GLASS CONTAINER */
        .block-container {{
            background: rgba(255,255,255,0.25);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            border: 1px solid rgba(255,255,255,0.4);
            padding: 2.5rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }}

        .block-container h1,
        .block-container h2,
        .block-container h3,
        .block-container h4,
        .block-container p,
        .block-container label {{
            color: black !important;
        }}

        input, textarea {{
            background-color: rgba(0,0,0,0.85) !important;
            color: white !important;
            border-radius: 10px !important;
        }}

        /* GLASS BUTTON */
        div[data-testid="stButton"] > button {{
            background: rgba(255,255,255,0.3) !important;
            backdrop-filter: blur(15px);
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,0.5) !important;
            color: black !important;
            font-weight: bold !important;
            padding: 12px !important;
            transition: all 0.3s ease;
        }}

        /* ✅ GREEN HOVER BUTTON */
        div[data-testid="stButton"] > button:hover {{
            background: #4CAF50 !important;
            color: white !important;
            border: 1px solid #4CAF50 !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }}

        div[data-testid="stButton"] > button:active {{
            transform: translateY(1px);
        }}

        </style>
    """, unsafe_allow_html=True)


add_bg_from_local("background.jpg")

st.title(" AI Face Attendance System")

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

# ===============================
# MARK ATTENDANCE
# ===============================

if menu == "Mark Attendance":

    st.header("📝 Mark Attendance")

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist)

    st.write(f"📅 {now.strftime('%d-%m-%Y')}  ⏰ {now.strftime('%H:%M:%S')}")

    st.subheader("📍 Capture Location")
    location_data = streamlit_geolocation()

    location = None

    if location_data and "latitude" in location_data:
        lat = location_data["latitude"]
        lon = location_data["longitude"]

        location = f"{lat},{lon}"

        st.success("✅ Location captured successfully")
        st.write(f"Latitude: {lat}")
        st.write(f"Longitude: {lon}")

    else:
        st.warning("Click the button above to capture location.")

    manual_location = st.text_input("If auto location fails, enter manually (lat,lon)")
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
            final_location = location if location else manual_location

            if not final_location:
                st.error("❌ Location not available.")
                st.stop()

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

                # GLOBAL 45 MIN COOLDOWN
                last_record = supabase.table("attendance") \
                    .select("*") \
                    .eq("roll_no", recognized_roll) \
                    .order("marked_at", desc=True) \
                    .limit(1) \
                    .execute()

                if last_record.data:

                    last_time = datetime.datetime.fromisoformat(
                        last_record.data[0]["marked_at"].replace("Z", "+00:00")
                    )

                    time_difference = (now - last_time).total_seconds() / 60

                    if time_difference < 45:
                        remaining = 45 - int(time_difference)
                        st.error(
                            f"⏳ You must wait {remaining} more minutes before marking attendance again."
                        )
                        st.stop()


                if location:
                    user_lat, user_lon = map(float, final_location.split(","))

                    within_radius, distance = is_within_radius(
                        user_lat,
                        user_lon,
                        COLLEGE_LAT,
                        COLLEGE_LON,
                        ALLOWED_RADIUS_METERS
                    )

                    distance = int(distance)

                    st.info(
                        f"📍 {recognized_name} is {distance} meters away from the college"
                    )

                    if not within_radius:
                        st.error(
                            f"❌ You are not allowed to mark attendance."
                        )
                        st.stop()

                else:
                    st.error("❌ Location not detected.")
                    st.stop()


                supabase.table("attendance").insert({
                    "roll_no": recognized_roll,
                    "name": recognized_name,
                    "subject": subject,
                    "date": now.date().isoformat(),
                    "time": now.strftime("%H:%M:%S"),
                    "marked_at": now.isoformat(),
                    "location": final_location
                }).execute()

                st.success(
                    f"✅ {recognized_name} is {distance} meters away from the college. "
                    "Attendance marked successfully!"
                )

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