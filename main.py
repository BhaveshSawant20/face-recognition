import os
import tempfile
import requests
import streamlit as st
from supabase import create_client
from deepface import DeepFace

# ===============================
# SUPABASE CLIENT
# ===============================
def get_supabase_client():
    if "SUPABASE_URL" in st.secrets:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
    else:
        from dotenv import load_dotenv
        load_dotenv()
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Supabase credentials missing")

    return create_client(supabase_url, supabase_key)

# ===============================
# LOAD REGISTERED USERS
# ===============================
def load_registered_users():
    supabase = get_supabase_client()
    response = supabase.table("faces_data").select("*").execute()
    return response.data if response.data else []

# ===============================
# IDENTIFY PERSON (DeepFace)
# ===============================
def identify_person(captured_image_path):
    supabase = get_supabase_client()
    users = load_registered_users()

    if not users:
        return None, None, "No registered faces found"

    best_match_name = None
    best_match_roll = None
    lowest_distance = float("inf")  # ✅ Fix: was 1.0 before

    for user in users:
        name = user["name"]
        roll_no = user["roll_no"]
        image_path = user.get("image_path")

        if not image_path:
            continue

        registered_image_path = None

        try:
            # ✅ Fix: handle both old (dict) and new (string) Supabase SDK
            url_data = supabase.storage.from_("faces").get_public_url(image_path)

            if isinstance(url_data, dict):
                image_url = url_data.get("publicUrl") or url_data.get("data", {}).get("publicUrl")
            else:
                image_url = str(url_data).strip()

            if not image_url or not image_url.startswith("http"):
                print(f"⚠️ Invalid URL for {name}: {image_url}")
                continue

            # Download registered image from Supabase
            response = requests.get(image_url, timeout=10)

            if response.status_code != 200:
                print(f"❌ Failed to fetch image for {name} — HTTP {response.status_code}")
                continue

            if len(response.content) < 1000:  # ✅ Fix: catch empty/broken images
                print(f"⚠️ Image too small for {name}, likely broken")
                continue

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(response.content)
                registered_image_path = tmp.name

            # DeepFace comparison
            result = DeepFace.verify(
                img1_path=captured_image_path,
                img2_path=registered_image_path,
                enforce_detection=False,
                model_name="Facenet"
            )

            distance = result.get("distance", 1.0)
            print(f"📊 {name} ({roll_no}): distance = {distance:.4f}")  # debug

            if distance < lowest_distance and distance < 0.6:  # ✅ Fix: was 0.45
                lowest_distance = distance
                best_match_name = name
                best_match_roll = roll_no

        except Exception as e:
            print(f"❌ Error verifying {name}: {e}")
            continue

        finally:
            # ✅ Always clean up temp file
            if registered_image_path and os.path.exists(registered_image_path):
                os.remove(registered_image_path)

    if best_match_name:
        print(f"✅ Best match: {best_match_name} with distance {lowest_distance:.4f}")
        return best_match_name, best_match_roll, "Match found"
    else:
        return None, None, "Face not recognized"