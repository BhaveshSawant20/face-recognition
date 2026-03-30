# import streamlit as st
# import streamlit.components.v1 as components
# import os
# import datetime
# import pandas as pd
# from PIL import Image
# from dotenv import load_dotenv
# from supabase import create_client
# import tempfile
# import pytz
# import base64
# import math
# import download_weights
# from streamlit_geolocation import streamlit_geolocation
#
# from main import identify_person
#
# # ===============================
# # CONFIG
# # ===============================
#
# load_dotenv()
# st.set_page_config(page_title="AI Attendance System", layout="centered")
#
# # ===============================
# # COLLEGE LOCATION CONFIG
# # ===============================
#
# COLLEGE_LAT = 19.26653217220706
# COLLEGE_LON = 72.97446013277826
# ALLOWED_RADIUS_METERS = 20000
#
#
# def is_within_radius(user_lat, user_lon, college_lat, college_lon, radius_m):
#     R = 6371000
#
#     phi1 = math.radians(user_lat)
#     phi2 = math.radians(college_lat)
#
#     delta_phi = math.radians(college_lat - user_lat)
#     delta_lambda = math.radians(college_lon - user_lon)
#
#     a = (
#         math.sin(delta_phi / 2) ** 2 +
#         math.cos(phi1) * math.cos(phi2) *
#         math.sin(delta_lambda / 2) ** 2
#     )
#
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     distance = R * c
#
#     return distance <= radius_m, distance
#
#
# # ===============================
# # BACKGROUND + GLASS STYLE + GREEN HOVER BUTTONS
# # ===============================
#
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
#         /* GLASS CONTAINER */
#         .block-container {{
#             background: rgba(255,255,255,0.25);
#             backdrop-filter: blur(20px);
#             border-radius: 25px;
#             border: 1px solid rgba(255,255,255,0.4);
#             padding: 2.5rem;
#             box-shadow: 0 8px 32px rgba(0,0,0,0.2);
#         }}
#
#         .block-container h1,
#         .block-container h2,
#         .block-container h3,
#         .block-container h4,
#         .block-container p,
#         .block-container label {{
#             color: black !important;
#         }}
#
#         input, textarea {{
#             background-color: rgba(0,0,0,0.85) !important;
#             color: white !important;
#             border-radius: 10px !important;
#         }}
#
#         /* GLASS BUTTON */
#         div[data-testid="stButton"] > button {{
#             background: rgba(255,255,255,0.3) !important;
#             backdrop-filter: blur(15px);
#             border-radius: 14px !important;
#             border: 1px solid rgba(255,255,255,0.5) !important;
#             color: black !important;
#             font-weight: bold !important;
#             padding: 12px !important;
#             transition: all 0.3s ease;
#         }}
#
#         /* ✅ GREEN HOVER BUTTON */
#         div[data-testid="stButton"] > button:hover {{
#             background: #4CAF50 !important;
#             color: white !important;
#             border: 1px solid #4CAF50 !important;
#             transform: translateY(-2px);
#             box-shadow: 0 8px 20px rgba(0,0,0,0.2);
#         }}
#
#         div[data-testid="stButton"] > button:active {{
#             transform: translateY(1px);
#         }}
#
#         </style>
#     """, unsafe_allow_html=True)
#
#
# add_bg_from_local("background.jpg")
#
# st.title(" AI Face Attendance System")
#
# # ===============================
# # SUPABASE
# # ===============================
#
# # SUPABASE_URL = os.getenv("SUPABASE_URL")
# # SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# #
# # if not SUPABASE_URL or not SUPABASE_KEY:
# #     st.error("Supabase environment variables missing")
# #     st.stop()
# #
# # supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
#
#
# if "SUPABASE_URL" in st.secrets:
#     SUPABASE_URL = st.secrets["SUPABASE_URL"]
#     SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
# else:
#     from dotenv import load_dotenv
#     load_dotenv()
#     SUPABASE_URL = os.getenv("SUPABASE_URL")
#     SUPABASE_KEY = os.getenv("SUPABASE_KEY")
#
# if not SUPABASE_URL or not SUPABASE_KEY:
#     st.error("❌ Supabase credentials missing")
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
# # REGISTER FACE
# # ===============================
#
# if menu == "Register Face":
#
#     st.header("📌 Register New Student")
#
#     full_name = st.text_input("Enter Full Name")
#     roll_no_input = st.text_input("Enter Roll No")
#     image_buffer = st.camera_input(
#         "Capture Face",
#         key=f"{menu}_camera"
#     )
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
#
#                     with open(tmp.name, "rb") as f:
#                         supabase.storage.from_("faces").upload(
#                             filename,
#                             f,
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
#
# if menu == "Mark Attendance":
#
#     st.header("📝 Mark Attendance")
#
#     ist = pytz.timezone("Asia/Kolkata")
#     now = datetime.datetime.now(ist)
#
#     st.write(f"📅 {now.strftime('%d-%m-%Y')}  ⏰ {now.strftime('%H:%M:%S')}")
#
#     st.subheader("📍 Capture Location")
#
#     # session state to control location capture
#     if "get_location" not in st.session_state:
#         st.session_state.get_location = False
#
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         if st.button("📍 Get My Location", use_container_width=True):
#             st.session_state.get_location = True
#
#     location = None
#
#     # Only run geolocation AFTER button click
#     if st.session_state.get_location:
#
#         location_data = streamlit_geolocation()
#
#         if location_data and location_data.get("latitude"):
#
#             lat = location_data["latitude"]
#             lon = location_data["longitude"]
#
#             location = f"{lat},{lon}"
#
#             st.success("✅ Location captured successfully")
#             st.write(f"Latitude: {lat}")
#             st.write(f"Longitude: {lon}")
#
#         else:
#             st.warning("Allow browser location permission.")
#
#     image_buffer = st.camera_input(
#         "Capture Face",
#         key=f"{menu}_camera"
#     )
#     roll_no_input = st.text_input("Enter Roll No")
#
#     subjects = ["SPCC", "CSS", "MC", "AI", "IOT", "CC", "MINI PROJECT"]
#     subject = st.radio(
#         "Select Lecture",
#         subjects,
#         horizontal=True,
#         index=None
#     )
#
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         mark_clicked = st.button("Mark Attendance", use_container_width=True)
#
#     if mark_clicked:
#
#         if not image_buffer or not roll_no_input:
#             st.warning("Capture image and enter roll number")
#             st.stop()
#
#         if not location:
#             st.error("❌ Location is required to mark attendance.")
#             st.stop()
#
#         if subject is None:
#             st.warning("Please select a subject")
#             st.stop()
#
#         final_location = location
#
#         # Safe parsing
#         try:
#             user_lat, user_lon = map(
#                 float,
#                 [x.strip() for x in final_location.split(",")]
#             )
#         except:
#             st.error("❌ Location format error.")
#             st.stop()
#
#         image = Image.open(image_buffer).convert("RGB")
#
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
#             image.save(tmp.name)
#             temp_path = tmp.name
#
#         recognized_name, recognized_roll, message = identify_person(temp_path)
#
#         if not recognized_name:
#             st.error(message)
#             st.stop()
#
#         if recognized_roll != roll_no_input.strip():
#             st.error("Roll number does not match recognized face ❌")
#             st.stop()
#
#         # ===============================
#         # GLOBAL 45 MIN COOLDOWN
#         # ===============================
#
#         last_record = supabase.table("attendance") \
#             .select("*") \
#             .eq("roll_no", recognized_roll) \
#             .order("marked_at", desc=True) \
#             .limit(1) \
#             .execute()
#
#         if last_record.data:
#
#             record = last_record.data[0]
#
#             timestamp = record.get("marked_at")
#
#             last_time = None
#             if timestamp:
#                 try:
#                     last_time = datetime.datetime.fromisoformat(
#                         str(timestamp).replace("Z", "+00:00")
#                     )
#
#                     # Convert UTC → IST
#                     last_time = last_time.astimezone(ist)
#
#                 except Exception:
#                     last_time = None
#
#             if last_time:
#                 time_difference = (now - last_time).total_seconds() / 60
#
#                 if time_difference < 45:
#                     remaining = 45 - int(time_difference)
#
#                     st.error(
#                         f"⏳ You must wait {remaining} more minutes before marking attendance again."
#                     )
#                     st.stop()
#
#         within_radius, distance = is_within_radius(
#             user_lat,
#             user_lon,
#             COLLEGE_LAT,
#             COLLEGE_LON,
#             ALLOWED_RADIUS_METERS
#         )
#
#         distance = int(distance)
#
#         st.info(
#             f"📍 {recognized_name} is {distance} meters away from the college"
#         )
#
#         if not within_radius:
#             st.error("❌ You are not allowed to mark attendance.")
#             st.stop()
#
#         supabase.table("attendance").insert({
#             "roll_no": recognized_roll,
#             "name": recognized_name,
#             "subject": subject,
#             "date": now.date().isoformat(),
#             "time": now.strftime("%H:%M:%S"),
#             "marked_at": now.isoformat(),
#             "location": final_location
#         }).execute()
#
#         st.success("✅ Attendance marked successfully!")
#
# # ===============================
# # VIEW ATTENDANCE
# # ===============================
#
# if menu == "View Attendance":
#
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
#         # Remove unwanted columns if they exist
#         df = df.drop(columns=["marked_at", "created_at", "id"], errors="ignore")
#
#         st.subheader("📋 Attendance Records")
#         st.dataframe(df, use_container_width=True)
#
#         st.subheader("📊 Subject Wise Attendance")
#         subject_count = df["subject"].value_counts()
#         st.bar_chart(subject_count)
#
#     else:
#         st.info("No attendance records found")
















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
import download_weights
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

COLLEGE_LAT = 19.26653217220706
COLLEGE_LON = 72.97446013277826
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
# GLASS POPUP — stores in session, rendered once at top
# ===============================

def show_popup(message, popup_type="success"):
    """Queue a popup to be shown. Rendered by render_popup() at page top."""
    st.session_state["_popup_message"] = message
    st.session_state["_popup_type"] = popup_type


def render_popup():
    """Call this once near the top of the page to render any queued popup."""
    if not st.session_state.get("_popup_message"):
        return

    message = st.session_state["_popup_message"]
    popup_type = st.session_state.get("_popup_type", "success")

    if popup_type == "success":
        btn_color = "#4CAF50"
        btn_shadow = "rgba(76,175,80,0.45)"
        icon = "✅"
        title = "Success"
    elif popup_type == "error":
        btn_color = "#f44336"
        btn_shadow = "rgba(244,67,54,0.45)"
        icon = "❌"
        title = "Error"
    elif popup_type == "warning":
        btn_color = "#FF9800"
        btn_shadow = "rgba(255,152,0,0.45)"
        icon = "⚠️"
        title = "Warning"
    elif popup_type == "info":
        btn_color = "#2196F3"
        btn_shadow = "rgba(33,150,243,0.45)"
        icon = "ℹ️"
        title = "Info"
    else:
        btn_color = "#4CAF50"
        btn_shadow = "rgba(76,175,80,0.45)"
        icon = "✅"
        title = "Done"

    # Use a unique key so Streamlit doesn't cache/skip re-renders
    popup_key = f"popup_{abs(hash(message + popup_type)) % 999999}"

    st.markdown(f"""
        <style>
        #{popup_key}_overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.55);
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        #{popup_key}_box {{
            background: rgba(255, 255, 255, 0.18);
            backdrop-filter: blur(30px) saturate(180%);
            -webkit-backdrop-filter: blur(30px) saturate(180%);
            border: 1.5px solid rgba(255, 255, 255, 0.55);
            border-radius: 24px;
            padding: 40px 48px;
            max-width: 400px;
            width: 90vw;
            text-align: center;
            box-shadow: 0 8px 40px rgba(0,0,0,0.3),
                        inset 0 1px 0 rgba(255,255,255,0.6);
            animation: glassPopIn 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        @keyframes glassPopIn {{
            from {{ transform: scale(0.82) translateY(24px); opacity: 0; }}
            to   {{ transform: scale(1)    translateY(0);    opacity: 1; }}
        }}
        #{popup_key}_icon  {{ font-size: 52px; line-height: 1; margin-bottom: 12px; }}
        #{popup_key}_title {{
            font-size: 20px; font-weight: 700; color: #fff;
            margin-bottom: 8px; text-shadow: 0 1px 6px rgba(0,0,0,0.35);
        }}
        #{popup_key}_msg {{
            font-size: 14px; color: rgba(255,255,255,0.88);
            margin-bottom: 28px; line-height: 1.6;
            white-space: pre-line; text-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }}
        #{popup_key}_btn {{
            background: {btn_color}; color: #fff; border: none;
            border-radius: 14px; padding: 12px 40px;
            font-size: 15px; font-weight: 700; cursor: pointer;
            box-shadow: 0 4px 18px {btn_shadow};
            letter-spacing: 0.3px;
            transition: transform 0.15s ease, opacity 0.15s ease;
        }}
        #{popup_key}_btn:hover  {{ opacity: 0.88; transform: translateY(-2px); }}
        #{popup_key}_btn:active {{ transform: translateY(1px); }}
        </style>

        <div id="{popup_key}_overlay">
            <div id="{popup_key}_box">
                <div id="{popup_key}_icon">{icon}</div>
                <div id="{popup_key}_title">{title}</div>
                <div id="{popup_key}_msg">{message}</div>
                <button id="{popup_key}_btn"
                    onclick="document.getElementById('{popup_key}_overlay').style.display='none'">
                    OK
                </button>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Clear after rendering so it doesn't persist on next rerun
    st.session_state["_popup_message"] = None
    st.session_state["_popup_type"] = None


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
        }}
        .block-container h1, .block-container h2,
        .block-container h3, .block-container h4,
        .block-container p,  .block-container label {{
            color: black !important;
        }}
        input, textarea {{
            background-color: rgba(0,0,0,0.85) !important;
            color: white !important;
            border-radius: 10px !important;
        }}
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

# ===============================
# RENDER POPUP (must be early, before any other content)
# ===============================

render_popup()

st.title("🎓 AI Face Attendance System")

# ===============================
# SUPABASE
# ===============================

if "SUPABASE_URL" in st.secrets:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
else:
    load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    show_popup("Supabase credentials missing! Check your secrets.", "error")
    st.rerun()

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
    image_buffer = st.camera_input("Capture Face", key=f"{menu}_camera")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        register_clicked = st.button("Register Student", use_container_width=True)

    if register_clicked:
        if not full_name or not roll_no_input or not image_buffer:
            show_popup("Please fill all fields and capture your face!", "warning")
            st.rerun()
        else:
            name = full_name.strip()
            roll_no = roll_no_input.strip()

            existing = supabase.table("faces_data") \
                .select("*").eq("roll_no", roll_no).execute()

            if existing.data:
                existing_name = existing.data[0]["name"]
                show_popup(f"Student '{existing_name}' is already registered!", "error")
                st.rerun()
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

                show_popup(f"Student {name} registered successfully! 🎉", "success")
                st.rerun()

# ===============================
# MARK ATTENDANCE
# ===============================

if menu == "Mark Attendance":

    st.header("📝 Mark Attendance")

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist)

    st.write(f"📅 {now.strftime('%d-%m-%Y')}  ⏰ {now.strftime('%H:%M:%S')}")

    st.subheader("📍 Capture Location")

    if "get_location" not in st.session_state:
        st.session_state.get_location = False

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📍 Get My Location", use_container_width=True):
            st.session_state.get_location = True

    location = None

    if st.session_state.get_location:
        location_data = streamlit_geolocation()

        if location_data and location_data.get("latitude"):
            lat = location_data["latitude"]
            lon = location_data["longitude"]
            location = f"{lat},{lon}"
            st.success("✅ Location captured successfully")
            st.write(f"Latitude: {lat}")
            st.write(f"Longitude: {lon}")
        else:
            st.warning("⚠️ Allow browser location permission and try again.")

    image_buffer = st.camera_input("Capture Face", key=f"{menu}_camera")
    roll_no_input = st.text_input("Enter Roll No")

    subjects = ["SPCC", "CSS", "MC", "AI", "IOT", "CC", "MINI PROJECT"]
    subject = st.radio("Select Lecture", subjects, horizontal=True, index=None)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mark_clicked = st.button("Mark Attendance", use_container_width=True)

    if mark_clicked:

        # --- Validation (popup + rerun, NO st.stop()) ---
        if not image_buffer or not roll_no_input:
            show_popup("Please capture your face and enter roll number!", "warning")
            st.rerun()

        if not location:
            show_popup("Location is required!\nClick 'Get My Location' first.", "error")
            st.rerun()

        if subject is None:
            show_popup("Please select a subject!", "warning")
            st.rerun()

        try:
            user_lat, user_lon = map(float, [x.strip() for x in location.split(",")])
        except Exception:
            show_popup("Location format error. Please try again.", "error")
            st.rerun()

        image = Image.open(image_buffer).convert("RGB")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            image.save(tmp.name)
            temp_path = tmp.name

        with st.spinner("🔍 Recognizing face..."):
            recognized_name, recognized_roll, message = identify_person(temp_path)

        if not recognized_name:
            show_popup("Face not recognized!\nPlease try again in better lighting. 💡", "error")
            st.rerun()

        if recognized_roll != roll_no_input.strip():
            show_popup("Roll number does not match the recognized face!", "error")
            st.rerun()

        # --- 45 min cooldown ---
        last_record = supabase.table("attendance") \
            .select("*") \
            .eq("roll_no", recognized_roll) \
            .order("marked_at", desc=True) \
            .limit(1) \
            .execute()

        if last_record.data:
            timestamp = last_record.data[0].get("marked_at")
            last_time = None
            if timestamp:
                try:
                    last_time = datetime.datetime.fromisoformat(
                        str(timestamp).replace("Z", "+00:00")
                    ).astimezone(ist)
                except Exception:
                    last_time = None

            if last_time:
                time_difference = (now - last_time).total_seconds() / 60
                if time_difference < 45:
                    remaining = 45 - int(time_difference)
                    show_popup(
                        f"Please wait {remaining} more minutes\nbefore marking attendance again! ⏳",
                        "warning"
                    )
                    st.rerun()

        # --- Location check ---
        within_radius, distance = is_within_radius(
            user_lat, user_lon, COLLEGE_LAT, COLLEGE_LON, ALLOWED_RADIUS_METERS
        )
        distance = int(distance)

        if not within_radius:
            show_popup(
                f"You are {distance}m away from college.\nMust be within {ALLOWED_RADIUS_METERS}m to mark attendance!",
                "error"
            )
            st.rerun()

        # --- Mark attendance ---
        supabase.table("attendance").insert({
            "roll_no": recognized_roll,
            "name": recognized_name,
            "subject": subject,
            "date": now.date().isoformat(),
            "time": now.strftime("%H:%M:%S"),
            "marked_at": now.isoformat(),
            "location": location
        }).execute()

        show_popup(
            f"Attendance marked for {recognized_name}!\nSubject: {subject} 🎉",
            "success"
        )
        st.rerun()

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
        df = df.drop(columns=["marked_at", "created_at", "id"], errors="ignore")

        st.subheader("📋 Attendance Records")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Subject Wise Attendance")
        subject_count = df["subject"].value_counts()
        st.bar_chart(subject_count)

    else:
        show_popup("No attendance records found yet!", "info")
        st.rerun()