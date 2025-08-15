import os
import uuid
from django.core.exceptions import ValidationError
from PIL import Image
from supabase import create_client

def validate_post_image(file):
    """
    Validate post image upload
    - Only JPEG/PNG allowed
    - Max size 5MB
    - Valid image format
    """
    # Check file size (5MB = 5 * 1024 * 1024 bytes)
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("Post image file size must be less than 5MB.")
    
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

def generate_post_image_filename(post_id, original_filename):
    """
    Generate unique filename for post image upload
    """
    file_extension = os.path.splitext(original_filename)[1].lower()
    unique_id = str(uuid.uuid4())
    return f"posts/{post_id}/{unique_id}{file_extension}"

def upload_post_image_to_supabase(file, filename):
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    bucket_name = os.getenv("SUPABASE_STORAGE_BUCKET", "myavatar")

    if not supabase_url or not supabase_key:
        raise Exception("Supabase URL and Service Role Key must be configured in environment variables.")

    try:
        supabase_client = create_client(supabase_url, supabase_key)

        # Read file bytes
        file_bytes = file.read()

        # Upload to Supabase
        result = supabase_client.storage.from_(bucket_name).upload(
            path=filename,
            file=file_bytes,
            file_options={
                "content-type": file.content_type,
                "cacheControl": "3600",
                "upsert": "true"
            }
        )

        if isinstance(result, dict) and "error" in result and result["error"] is not None:
            raise Exception(result["error"]["message"])

        # Get public URL
        public_url = supabase_client.storage.from_(bucket_name).get_public_url(filename)
        return public_url

    except Exception as e:
        raise Exception(f"Failed to upload post image: {str(e)}")

def process_post_image_upload(file, post_id):
    """
    Process post image upload: validate, generate filename, upload to storage
    """
    # Validate file
    validate_post_image(file)
    
    # Generate unique filename
    filename = generate_post_image_filename(post_id, file.name)
    
    # Upload to Supabase Storage
    image_url = upload_post_image_to_supabase(file, filename)
    
    return image_url
