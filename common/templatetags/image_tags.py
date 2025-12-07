"""
Custom template tags for optimized image rendering.

Usage in templates:
    {% load image_tags %}
    
    {% responsive_image "path/to/image.jpg" "Alt text" %}
    {% lazy_image "path/to/image.jpg" "Alt text" class="img-fluid" %}
    {% cdn_image "static/logo.png" width=300 %}
"""

from typing import Optional
from django import template
from django.utils.html import format_html
from common.image_optimization import (
    CDNHelper,
    generate_picture_tag,
)

register = template.Library()


@register.simple_tag
def responsive_image(
    image_path: str,
    alt_text: str = "",
    sizes: str = "xs,sm,md,lg",
    css_class: str = "img-fluid",
    lazy: bool = True,
):
    """
    Generate responsive <picture> tag with WebP support.

    Usage:
        {% responsive_image "images/hero.jpg" "Hero image" sizes="sm,md,lg" %}
    """
    size_list = [s.strip() for s in sizes.split(",")]
    picture_html = generate_picture_tag(
        image_path,
        alt_text,
        sizes=size_list,
        lazy=lazy,
        css_class=css_class,
    )
    # generate_picture_tag zaten format_html ile güvenli HTML döndürür.
    return picture_html


@register.simple_tag
def lazy_image(
    image_path: str,
    alt_text: str = "",
    css_class: str = "",
    placeholder: str = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"%3E%3C/svg%3E',
):
    """
    Generate lazy-loaded image with placeholder.

    Usage:
        {% lazy_image "images/product.jpg" "Product photo" class="img-thumbnail" %}
    """
    return format_html(
        '<img src="{}" data-src="{}" alt="{}" class="lazy {}" loading="lazy">',
        placeholder,
        image_path,
        alt_text,
        css_class,
    )


@register.simple_tag
def cdn_image(
    image_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    format: str = "auto",
    alt_text: str = "",
    css_class: str = "",
):
    """
    Generate CDN-optimized image URL.

    Usage:
        {% cdn_image "static/logo.png" width=300 format="webp" %}
    """
    cdn_url = CDNHelper.get_image_cdn_url(
        image_path,
        width=width,
        height=height,
        format=format,
    )

    if alt_text or css_class:
        return format_html(
            '<img src="{}" alt="{}" class="{}" loading="lazy">',
            cdn_url,
            alt_text,
            css_class,
        )

    return cdn_url


@register.simple_tag
def webp_image(image_path: str, alt_text: str = "", css_class: str = ""):
    """
    Generate <picture> tag with WebP and fallback.

    Usage:
        {% webp_image "images/banner.jpg" "Banner" class="w-100" %}
    """
    import os

    base, ext = os.path.splitext(image_path)
    webp_path = f"{base}.webp"

    return format_html(
        """
    <picture>
        <source type="image/webp" srcset="{}">
        <source type="image/{}" srcset="{}">
        <img src="{}" alt="{}" class="{}" loading="lazy">
    </picture>
    """,
        webp_path,
        ext[1:],
        image_path,
        image_path,
        alt_text,
        css_class,
    )


@register.filter
def optimize_image_url(image_url: str, max_width: int = 1920) -> str:
    """
    Filter to optimize image URL through CDN.

    Usage:
        <img src="{{ product.image.url|optimize_image_url:800 }}">
    """
    return CDNHelper.get_image_cdn_url(image_url, width=max_width)
