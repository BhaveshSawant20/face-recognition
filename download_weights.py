import os
import requests
import streamlit as st

WEIGHTS_DIR = os.path.expanduser("~/.deepface/weights")
WEIGHTS_PATH = os.path.join(WEIGHTS_DIR, "facenet_weights.h5")
EXPECTED_SIZE = 90000000  # 90MB minimum


def preload_facenet_weights():
    os.makedirs(WEIGHTS_DIR, exist_ok=True)

    # Check if already downloaded correctly
    if os.path.exists(WEIGHTS_PATH):
        size = os.path.getsize(WEIGHTS_PATH)
        if size > EXPECTED_SIZE:
            print(f"✅ Facenet weights already present ({size} bytes)")
            return
        else:
            print(f"⚠️ Corrupted weights ({size} bytes), re-downloading...")
            os.remove(WEIGHTS_PATH)

    # ⬇️ YOUR GOOGLE DRIVE FILE ID HERE
    FILE_ID = "https://drive.google.com/file/d/1NjqIpPiDAHND_r15N7lOQhurpulfNgpV/view?usp=sharing"

    print("⬇️ Downloading Facenet weights from Google Drive...")

    try:
        # Step 1: Get confirmation token (for large files)
        session = requests.Session()
        URL = "https://drive.google.com/uc?export=download"

        response = session.get(URL, params={"id": FILE_ID}, stream=True)

        # Extract confirmation token if present
        token = None
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                token = value
                break

        if token:
            response = session.get(
                URL,
                params={"id": FILE_ID, "confirm": token},
                stream=True
            )

        # Save file
        with open(WEIGHTS_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)

        size = os.path.getsize(WEIGHTS_PATH)
        if size > EXPECTED_SIZE:
            print(f"✅ Weights downloaded successfully ({size} bytes)")
        else:
            print(f"❌ Download incomplete ({size} bytes) — check sharing settings")
            os.remove(WEIGHTS_PATH)

    except Exception as e:
        print(f"❌ Exception: {e}")


