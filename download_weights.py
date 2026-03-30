import os
import requests
from pathlib import Path

def preload_models():
    weights_dir = Path.home() / ".deepface" / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)
    weights_path = weights_dir / "facenet_weights.h5"

    # If file exists but is too small (corrupted), delete it
    if weights_path.exists() and weights_path.stat().st_size < 1_000_000:
        print(f"⚠️ Corrupted weights detected ({weights_path.stat().st_size} bytes), deleting...")
        weights_path.unlink()

    if not weights_path.exists():
        print("⬇️ Downloading Facenet weights from direct mirror...")

        # Direct download URL (bypasses GitHub redirect)
        url = "https://github.com/serengil/deepface_models/releases/download/v1.0/facenet_weights.h5"

        headers = {"Accept": "application/octet-stream"}
        response = requests.get(url, headers=headers, stream=True, allow_redirects=True)

        if response.status_code == 200:
            total = 0
            with open(weights_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    total += len(chunk)
            print(f"✅ Downloaded {total / 1_000_000:.1f} MB")
        else:
            print(f"❌ Download failed: {response.status_code}")
            return

    print(f"✅ Weights ready: {weights_path.stat().st_size / 1_000_000:.1f} MB")

    # Now preload into DeepFace
    try:
        import numpy as np
        from PIL import Image
        import tempfile
        from deepface import DeepFace

        dummy_img = np.zeros((160, 160, 3), dtype=np.uint8)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            Image.fromarray(dummy_img).save(tmp.name)
            tmp_path = tmp.name

        DeepFace.represent(
            img_path=tmp_path,
            model_name="Facenet",
            enforce_detection=False
        )
        print("✅ Facenet model loaded successfully!")

    except Exception as e:
        print(f"⚠️ Model load warning: {e}")

preload_models()