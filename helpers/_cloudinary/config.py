import cloudinary
from django.conf import settings

CLOUDINARY_CLOUD_NAME = settings.CLOUDINARY_CLOUD_NAME
CLOUDINARY_PUBLIC_API_KEY = settings.CLOUDINARY_PUBLIC_API_KEY
CLOUDINARY_SECRET_API_KEY = settings.CLOUDINARY_SECRET_API_KEY


# // Configuration
def cloudinary_init():
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_PUBLIC_API_KEY,
        api_secret=CLOUDINARY_SECRET_API_KEY,  # Click 'View API Keys' above to copy your API secret
        secure=True
    )
