# users/utils/avatar.py
import os
import uuid
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
import io
from supabase import create_client

def validate_avatar_file(file):
    """
    Validate avatar file upload
    - Only JPEG/PNG allowed
    - Max size 2MB
    - Valid image format
    """
    # Check file size (2MB = 2 * 1024 * 1024 bytes)
    if file.size > 2 * 1024 * 1024:
        raise ValidationError("Avatar file size must be less than 2MB.")
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    file_extension = os.path.splitext(file.name)[1].lower()
    if file_extension not in allowed_extensions:
        raise ValidationError("Only JPEG and PNG files are allowed.")
    
    # Validate image format
    try:
        image = Image.open(file)
        image.verify()
        file.seek(0)  # Reset file pointer
    except Exception:
        raise ValidationError("Invalid image file.")
    
    return True

def generate_avatar_filename(user_id, original_filename):
    """
    Generate unique filename for avatar upload
    """
    file_extension = os.path.splitext(original_filename)[1].lower()
    unique_id = str(uuid.uuid4())
    return f"avatars/{user_id}/{unique_id}{file_extension}"

def upload_to_supabase_storage(file, filename):
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # ✅ Use Service Role Key
    bucket_name = os.getenv("SUPABASE_STORAGE_BUCKET", "avatars")

    print(f"[DEBUG] Supabase URL: {supabase_url}")
    print(f"[DEBUG] Bucket Name: {bucket_name}")
    print(f"[DEBUG] Uploading File: {filename}")
    print(f"[DEBUG] File Content Type: {file.content_type}")

    if not supabase_url or not supabase_key:
        raise Exception("Supabase URL and Service Role Key must be configured in environment variables.")

    try:
        supabase_client = create_client(supabase_url, supabase_key)

        # Read file bytes
        file_bytes = file.read()
        print(f"[DEBUG] File Size: {len(file_bytes)} bytes")

        # Upload to Supabase
        result = supabase_client.storage.from_(bucket_name).upload(
            path=filename,
            file=file_bytes,
            file_options={
                "content-type": file.content_type,
                "cacheControl": "3600",
                "upsert": "true"  # ✅ must be string, not bool
            }
        )

        print(f"[DEBUG] Upload Result: {result}")

        if isinstance(result, dict) and "error" in result and result["error"] is not None:
            raise Exception(result["error"]["message"])

        # Get public URL
        public_url = supabase_client.storage.from_(bucket_name).get_public_url(filename)
        print(f"[DEBUG] Public URL: {public_url}")

        return public_url

    except Exception as e:
        print(f"[ERROR] Avatar upload failed: {str(e)}")
        raise Exception(f"Failed to upload avatar: {str(e)}")


def process_avatar_upload(file, user_id):
    """
    Process avatar upload: validate, generate filename, upload to storage
    """
    # Validate file
    validate_avatar_file(file)
    
    # Generate unique filename
    filename = generate_avatar_filename(user_id, file.name)
    
    # Upload to Supabase Storage
    avatar_url = upload_to_supabase_storage(file, filename)
    
    return avatar_url
