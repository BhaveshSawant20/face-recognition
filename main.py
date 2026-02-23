import os
import tempfile
from supabase import create_client
from deepface import DeepFace
import requests

# ===============================
# SUPABASE CLIENT
# ===============================
def get_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Supabase environment variables not set")

    return create_client(supabase_url, supabase_key)


# ===============================
# LOAD REGISTERED USERS
# ===============================
def load_registered_users():
    supabase = get_supabase_client()
    response = supabase.table("faces_data").select("*").execute()
    if response.data:
        return response.data
    return []


# ===============================
# IDENTIFY PERSON (DeepFace) — BEST MATCH
# ===============================
def identify_person(captured_image_path):
    supabase = get_supabase_client()
    users = load_registered_users()

    if len(users) == 0:
        return None, None, "No registered faces found"

    best_match_name = None
    best_match_roll = None
    lowest_distance = 1.0  # maximum possible distance

    for user in users:
        name = user["name"]
        roll_no = user["roll_no"]
        image_path = user.get("image_path")

        if not image_path:
            continue

        try:
            # Get public URL for the registered image
            url_data = supabase.storage.from_("faces").get_public_url(image_path)
            image_url = url_data.get('publicUrl') if isinstance(url_data, dict) else url_data
            if not image_url:
                continue

            # Download registered image temporarily
            response = requests.get(image_url)
            if response.status_code != 200:
                print(f"Failed to fetch image for {name}")
                continue

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(response.content)
                registered_image_path = tmp.name

            # Compare using DeepFace
            result = DeepFace.verify(
                img1_path=captured_image_path,
                img2_path=registered_image_path,
                enforce_detection=False,
                model_name='Facenet'
            )

            distance = result.get('distance', 1.0)
            if distance < lowest_distance and distance < 0.45:  # threshold for match
                lowest_distance = distance
                best_match_name = name
                best_match_roll = roll_no

        except Exception as e:
            print(f"Error verifying {name}: {e}")
            continue

    if best_match_name and best_match_roll:
        return best_match_name, best_match_roll, "Match found"
    else:
        return None, None, "Face not recognized"