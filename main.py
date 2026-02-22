# import cv2
# import numpy as np
# import os
# from datetime import datetime
# import face_recognition
# from cloud_face_loader import download_faces
# from firebase_config import db
# import streamlit as st
# import time
#
#
# # ---------------- LOAD FACES (SUPER CACHED) ---------------- #
# @st.cache_resource(show_spinner="Encoding faces... Please wait.")
# def load_known_faces():
#
#     download_faces()
#     faces_folder = "cloud_faces"
#
#     if not os.path.exists(faces_folder):
#         raise Exception("cloud_faces folder missing.")
#
#     known_encodings = []
#     known_names = []
#
#     for file in os.listdir(faces_folder):
#
#         if file.lower().endswith((".png", ".jpg", ".jpeg")):
#
#             path = os.path.join(faces_folder, file)
#             image = face_recognition.load_image_file(path)
#
#             encodings = face_recognition.face_encodings(image)
#
#             if encodings:
#                 known_encodings.append(encodings[0])
#                 known_names.append(os.path.splitext(file)[0].capitalize())
#
#     if not known_encodings:
#         raise Exception("No valid face encodings found.")
#
#     return known_encodings, known_names
#
#
# # ---------------- ATTENDANCE ENGINE ---------------- #
# def run_attendance_frame(frame_placeholder):
#
#     if 'stop_camera' not in st.session_state:
#         st.session_state.stop_camera = False
#
#     known_face_encodings, known_face_names = load_known_faces()
#
#     # prevents duplicate marking
#     students_marked = set()
#
#     cap = cv2.VideoCapture(0)
#
#     # ⭐ Better camera quality
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)   # 1280 causes lag on many laptops
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
#
#     cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
#
#     if not cap.isOpened():
#         st.error("Camera not accessible.")
#         return
#
#     info_box = st.empty()
#     info_box.info("🚀 Attendance running...")
#
#     try:
#
#         while cap.isOpened():
#
#             if st.session_state.stop_camera:
#                 info_box.warning("Camera stopped.")
#                 break
#
#             ret, frame = cap.read()
#
#             if not ret:
#                 info_box.error("Camera read failure.")
#                 break
#
#             # ---------- FAST FACE DETECTION ----------
#             small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#
#             rgb_small = cv2.cvtColor(
#                 small_frame,
#                 cv2.COLOR_BGR2RGB
#             )
#
#             face_locations = face_recognition.face_locations(rgb_small, model="hog")
#             face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
#
#             for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#
#                 name = "Unknown"
#                 confidence_text = ""
#
#                 distances = face_recognition.face_distance(
#                     known_face_encodings,
#                     face_encoding
#                 )
#
#                 if len(distances) > 0:
#
#                     best_index = np.argmin(distances)
#                     confidence = 1 - distances[best_index]
#
#                     # ⭐ Dynamic threshold (better than fixed tolerance)
#                     if confidence > 0.48:
#                         name = known_face_names[best_index]
#                         confidence_text = f"{int(confidence*100)}%"
#
#                         # ---------- FIRESTORE PROTECTION ----------
#                         if name not in students_marked:
#
#                             students_marked.add(name)
#
#                             now = datetime.now()
#
#                             db.collection("attendance").add({
#                                 "name": name,
#                                 "date": now.strftime("%Y-%m-%d"),
#                                 "time": now.strftime("%H:%M:%S"),
#                                 "timestamp": now
#                             })
#
#                             info_box.success(f"{name} marked present ✅")
#
#                 # ---------- DRAW UI ----------
#                 top *= 4
#                 right *= 4
#                 bottom *= 4
#                 left *= 4
#
#                 color = (0,255,0) if name != "Unknown" else (0,0,255)
#
#                 cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
#                 cv2.rectangle(frame, (left, bottom-35), (right, bottom), color, cv2.FILLED)
#
#                 label = f"{name} {confidence_text}" if name!="Unknown" else name
#
#                 cv2.putText(
#                     frame,
#                     label,
#                     (left+6, bottom-6),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.7,
#                     (255,255,255),
#                     2
#                 )
#
#             # ⭐ CRITICAL — fills container properly
#             frame_placeholder.image(
#                 frame,
#                 channels="BGR",
#                 use_container_width=True
#             )
#
#             # controls CPU usage
#             time.sleep(0.008)
#
#     finally:
#         cap.release()
#         st.session_state.stop_camera = False
#         info_box.success("Attendance session ended.")

def process_image():
    import cv2
import numpy as np
import mediapipe as mp
from supabase import create_client
import os


# ===============================
# SUPABASE CLIENT
# ===============================

def get_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Supabase environment variables not set.")

    return create_client(supabase_url, supabase_key)


# ===============================
# FACE DETECTION USING MEDIAPIPE
# ===============================

mp_face = mp.solutions.face_detection

def detect_face(image_np):
    with mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detector:
        results = face_detector.process(cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
        return results.detections if results.detections else []


# ===============================
# SIMPLE FACE ENCODING STORAGE
# (Cloud friendly approach)
# ===============================

def load_known_faces():
    supabase = get_supabase_client()

    response = supabase.table("faces_data").select("*").execute()

    known_encodings = []
    known_names = []

    if response.data:
        for item in response.data:
            known_encodings.append(np.array(item["encoding"]))
            known_names.append(item["name"])

    return known_encodings, known_names


def recognize_face(image_np):

    known_encodings, known_names = load_known_faces()

    if not known_encodings:
        return "No registered faces."

    # Simple vector matching
    detections = detect_face(image_np)

    if not detections:
        return "No face detected."

    # Generate dummy embedding (cloud safe approximation)
    face_vector = np.mean(image_np, axis=(0, 1))

    distances = [np.linalg.norm(face_vector - enc) for enc in known_encodings]

    best_index = int(np.argmin(distances))

    if distances[best_index] < 50:
        return f"Welcome {known_names[best_index]}"

    return "Face not recognized"