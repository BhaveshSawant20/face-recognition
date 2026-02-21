import os
import httpx
from supabase_config import supabase


FOLDER = "cloud_faces"
BUCKET = "faces"


def download_faces():

    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    print("Syncing faces from Supabase...")

    files = supabase.storage.from_(BUCKET).list()

    if not files:
        raise Exception("No faces found in Supabase bucket.")


    for file in files:

        file_name = file['name']
        local_path = os.path.join(FOLDER, file_name)

        # ✅ Skip if already cached
        if os.path.exists(local_path):
            continue

        public_url = supabase.storage.from_(BUCKET).get_public_url(file_name)

        response = httpx.get(public_url)

        if response.status_code == 200:

            with open(local_path, "wb") as f:
                f.write(response.content)

            print(f"Downloaded -> {file_name}")

        else:
            print(f"Failed -> {file_name}")
