"""
Middleware for automatic image optimization.

Features:
- Auto-convert uploaded images to WebP
- Resize large uploads
- Add lazy loading to HTML responses
"""

import re
import logging
from django.conf import settings
from apps.common.image_optimization import ImageOptimizer

logger = logging.getLogger(__name__)


class ImageOptimizationMiddleware:
    """
    Automatically optimize uploaded images.

    Add to MIDDLEWARE in settings:
        'apps.common.middleware.image_middleware.ImageOptimizationMiddleware',
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.optimizer = ImageOptimizer()
        self.max_upload_size = getattr(settings, "MAX_IMAGE_SIZE", (1920, 1080))

    def __call__(self, request):
        # Optimize uploaded images in request.FILES
        if request.FILES:
            for field_name, uploaded_file in request.FILES.items():
                if self._is_image(uploaded_file):
                    try:
                        optimized = self.optimizer.optimize_uploaded_file(
                            uploaded_file,
                            max_size=self.max_upload_size,
                        )
                        request.FILES[field_name] = optimized
                    except Exception as e:
                        logger.error(f"Image optimization failed for {field_name}: {e}")

        response = self.get_response(request)

        return response

    def _is_image(self, file) -> bool:
        """Check if uploaded file is an image."""
        if hasattr(file, "content_type"):
            return file.content_type.startswith("image/")
        return False


class LazyLoadingMiddleware:
    """
    Automatically add lazy loading to <img> tags in HTML responses.

    Add to MIDDLEWARE in settings:
        'apps.common.middleware.image_middleware.LazyLoadingMiddleware',
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Regex to find <img> tags without loading attribute
        self.img_pattern = re.compile(r"<img(?![^>]*loading=)([^>]*)>", re.IGNORECASE)

    def __call__(self, request):
        response = self.get_response(request)

        # Only process HTML responses
        if response.get("Content-Type", "").startswith("text/html") and hasattr(
            response, "content"
        ):
            try:
                content = response.content.decode("utf-8")

                # Add loading="lazy" to all <img> tags
                modified_content = self.img_pattern.sub(
                    r'<img\1 loading="lazy">', content
                )

                response.content = modified_content.encode("utf-8")

            except Exception as e:
                logger.error(f"LazyLoadingMiddleware failed: {e}")

        return response
