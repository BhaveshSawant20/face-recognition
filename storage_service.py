from supabase_config import supabase

def upload_face(file_path, file_name):

    with open(file_path, "rb") as f:
        supabase.storage.from_("faces").upload(
            path=file_name,
            file=f
        )

    url = supabase.storage.from_("faces").get_public_url(file_name)

    return url
