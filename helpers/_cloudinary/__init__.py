from .config import cloudinary_init
from .services import get_cloudinary_image_object, get_cloudinary_video_object


cloudinary_init()

__all__ = [
    'cloudinary_init',
    'get_cloudinary_image_object',
    'get_cloudinary_video_object'
          ]
