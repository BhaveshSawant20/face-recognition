from deepface import DeepFace
import os


# Pre-download Facenet weights at build time
def preload_models():
    import numpy as np
    dummy_img = np.zeros((160, 160, 3), dtype=np.uint8)

    import tempfile
    from PIL import Image

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        Image.fromarray(dummy_img).save(tmp.name)
        tmp_path = tmp.name

    try:
        DeepFace.represent(
            img_path=tmp_path,
            model_name="Facenet",
            enforce_detection=False
        )
        print("✅ Facenet weights loaded successfully")
    except Exception as e:
        print(f"⚠️ Preload warning: {e}")


preload_models()