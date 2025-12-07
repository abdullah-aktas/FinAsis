"""
Image optimization utilities for performance.

Features:
- WebP conversion with fallback
- Responsive image generation
- Lazy loading helpers
- Image compression
- CDN URL generation
"""
import logging
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from PIL import Image, ImageOps
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.html import format_html
from django.templatetags.static import static

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """
    Optimize images for web delivery.

    Features:
    - Convert to WebP with fallback formats
    - Generate responsive sizes
    - Compress while maintaining quality
    - Progressive/interlaced encoding
    """

    # Responsive breakpoints (Bootstrap-style)
    RESPONSIVE_SIZES = {
        "xs": 576,  # Mobile
        "sm": 768,  # Tablet
        "md": 992,  # Desktop
        "lg": 1200,  # Large desktop
        "xl": 1920,  # Full HD
    }

    # WebP quality settings
    WEBP_QUALITY = 85
    JPEG_QUALITY = 85
    PNG_OPTIMIZE = True

    def __init__(self, quality: int = 85):
        """
        Initialize optimizer with quality setting.

        Args:
            quality: JPEG/WebP quality (1-100, default 85)
        """
        self.quality = quality

    def optimize_image(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        max_size: Optional[Tuple[int, int]] = None,
        convert_to_webp: bool = True,
    ) -> Dict[str, str]:
        """
        Optimize single image.

        Args:
            image_path: Path to source image
            output_path: Output directory (default: same as source)
            max_size: Maximum dimensions (width, height)
            convert_to_webp: Generate WebP version

        Returns:
            Dictionary with paths: {'original': ..., 'webp': ..., 'optimized': ...}
        """
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB for JPEG
                if img.mode == "RGBA" and not convert_to_webp:
                    # Create white background
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(
                        img, mask=img.split()[3]
                    )  # Use alpha channel as mask
                    img = background
                elif img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")

                # Resize if needed
                if max_size:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Auto-rotate based on EXIF
                img = ImageOps.exif_transpose(img)

                # Determine output paths
                input_path = Path(image_path)
                output_dir = Path(output_path) if output_path else input_path.parent
                output_dir.mkdir(parents=True, exist_ok=True)

                base_name = input_path.stem
                results = {"original": str(image_path)}

                # Save optimized JPEG/PNG
                ext = input_path.suffix.lower()
                if ext in [".jpg", ".jpeg"]:
                    optimized_path = output_dir / f"{base_name}_optimized.jpg"
                    img.save(
                        optimized_path,
                        "JPEG",
                        quality=self.quality,
                        optimize=True,
                        progressive=True,
                    )
                    results["optimized"] = str(optimized_path)
                elif ext == ".png":
                    optimized_path = output_dir / f"{base_name}_optimized.png"
                    img.save(
                        optimized_path,
                        "PNG",
                        optimize=self.PNG_OPTIMIZE,
                    )
                    results["optimized"] = str(optimized_path)

                # Generate WebP version
                if convert_to_webp:
                    webp_path = output_dir / f"{base_name}.webp"
                    img.save(
                        webp_path,
                        "WEBP",
                        quality=self.WEBP_QUALITY,
                        method=6,  # Maximum compression
                    )
                    results["webp"] = str(webp_path)

                return results

        except Exception as e:
            logger.error(f"Image optimization failed for {image_path}: {e}")
            return {"original": str(image_path)}

    def generate_responsive_images(
        self,
        image_path: str,
        output_dir: Optional[str] = None,
        sizes: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, str]]:
        """
        Generate responsive image sizes.

        Args:
            image_path: Source image path
            output_dir: Output directory
            sizes: List of size keys (default: all RESPONSIVE_SIZES)

        Returns:
            Dictionary: {size_key: {'jpg': path, 'webp': path}}
        """
        if sizes is None:
            sizes = list(self.RESPONSIVE_SIZES.keys())

        results = {}
        input_path = Path(image_path)
        output_path = Path(output_dir) if output_dir else input_path.parent

        try:
            with Image.open(image_path) as img:
                original_width, original_height = img.size
                aspect_ratio = original_height / original_width

                for size_key in sizes:
                    max_width = self.RESPONSIVE_SIZES[size_key]

                    # Skip if image is smaller than breakpoint
                    if original_width < max_width:
                        continue

                    max_height = int(max_width * aspect_ratio)

                    # Generate for this size
                    size_results = self.optimize_image(
                        image_path,
                        output_path=str(output_path / size_key),
                        max_size=(max_width, max_height),
                        convert_to_webp=True,
                    )

                    results[size_key] = size_results

            return results

        except Exception as e:
            logger.error(f"Responsive image generation failed for {image_path}: {e}")
            return {}

    def optimize_uploaded_file(
        self,
        uploaded_file: InMemoryUploadedFile,
        max_size: Tuple[int, int] = (1920, 1080),
    ) -> InMemoryUploadedFile:
        """
        Optimize uploaded file before saving.

        Args:
            uploaded_file: Django uploaded file
            max_size: Maximum dimensions

        Returns:
            Optimized InMemoryUploadedFile
        """
        try:
            img = Image.open(uploaded_file)

            # Convert mode if needed
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            # Resize
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Auto-rotate
            img = ImageOps.exif_transpose(img)

            # Save to BytesIO
            output = BytesIO()
            img_format = img.format or "JPEG"

            if img_format == "JPEG":
                img.save(output, format="JPEG", quality=self.quality, optimize=True)
            elif img_format == "PNG":
                img.save(output, format="PNG", optimize=True)
            else:
                img.save(output, format=img_format)

            output.seek(0)

            # Create new InMemoryUploadedFile
            return InMemoryUploadedFile(
                output,
                "ImageField",
                uploaded_file.name,
                uploaded_file.content_type,
                output.getbuffer().nbytes,
                None,
            )

        except Exception as e:
            logger.error(f"Uploaded file optimization failed: {e}")
            return uploaded_file


class CDNHelper:
    """
    CDN URL generation and management.

    Supports:
    - CloudFlare
    - AWS CloudFront
    - Custom CDN
    """

    @staticmethod
    def get_cdn_url(path: str, cdn_provider: str = "cloudflare") -> str:
        """
        Generate CDN URL for static/media file.

        Args:
            path: Relative path to file
            cdn_provider: CDN provider name

        Returns:
            Full CDN URL
        """
        cdn_domain = getattr(settings, "CDN_DOMAIN", None)

        if not cdn_domain:
            # Fallback to local static URL
            return static(path)

        # Remove leading slash
        path = path.lstrip("/")

        if cdn_provider == "cloudflare":
            # CloudFlare R2 or CDN
            return f"https://{cdn_domain}/{path}"
        elif cdn_provider == "cloudfront":
            # AWS CloudFront
            return f"https://{cdn_domain}/{path}"
        else:
            # Generic CDN
            return f"https://{cdn_domain}/{path}"

    @staticmethod
    def get_image_cdn_url(
        path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        format: str = "auto",
    ) -> str:
        """
        Generate CDN URL with image transformation parameters.

        Args:
            path: Image path
            width: Resize width
            height: Resize height
            format: Output format (auto, webp, jpeg, png)

        Returns:
            CDN URL with transformation params
        """
        base_url = CDNHelper.get_cdn_url(path)

        # CloudFlare Image Resizing parameters
        params = []
        if width:
            params.append(f"width={width}")
        if height:
            params.append(f"height={height}")
        if format != "auto":
            params.append(f"format={format}")

        if params:
            return f"{base_url}?{('&').join(params)}"

        return base_url


def generate_picture_tag(
    image_path: str,
    alt_text: str,
    sizes: Optional[List[str]] = None,
    lazy: bool = True,
    css_class: str = "",
) -> str:
    """
    Generate responsive <picture> tag with WebP support.

    Args:
        image_path: Path to image
        alt_text: Alt text for accessibility
        sizes: Responsive sizes to include
        lazy: Enable lazy loading
        css_class: CSS classes

    Returns:
        HTML <picture> tag
    """
    if sizes is None:
        sizes = ["xs", "sm", "md", "lg"]

    optimizer = ImageOptimizer()
    base_path = Path(image_path)
    base_name = base_path.stem

    # Generate sources
    sources = []

    # WebP sources
    for size in sizes:
        width = optimizer.RESPONSIVE_SIZES[size]
        webp_path = f"{base_path.parent}/{size}/{base_name}.webp"
        sources.append(
            f'<source media="(max-width: {width}px)" type="image/webp" srcset="{webp_path}">'
        )

    # JPEG/PNG fallback sources
    for size in sizes:
        width = optimizer.RESPONSIVE_SIZES[size]
        fallback_path = (
            f"{base_path.parent}/{size}/{base_name}_optimized{base_path.suffix}"
        )
        sources.append(
            f'<source media="(max-width: {width}px)" srcset="{fallback_path}">'
        )

    # Build <picture> tag
    loading_attr = 'loading="lazy"' if lazy else ""

    return format_html(
        '<picture>{}<img src="{}" alt="{}" class="{}" {}></picture>',
        "".join(sources),
        image_path,
        alt_text,
        css_class,
        loading_attr,
    )
