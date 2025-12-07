from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

from common.seo import STATIC_PAGES


class Command(BaseCommand):
    help = "Generate a sitemap.xml file based on configured static SEO pages."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--output",
            dest="output",
            default=None,
            help="Custom output path for sitemap.xml (defaults to project root).",
        )
        parser.add_argument(
            "--base-url",
            dest="base_url",
            default=None,
            help="Override the SITE_BASE_URL setting when generating absolute URLs.",
        )

    def handle(self, *args, **options) -> None:
        base_url = options.get("base_url") or getattr(
            settings, "SITE_BASE_URL", "https://finasis.com"
        )
        base_url = base_url.rstrip("/")

        output_arg = options.get("output")
        if output_arg:
            output_path = Path(output_arg)
        else:
            output_path = Path(settings.BASE_DIR).parent / "sitemap.xml"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]

        for page in STATIC_PAGES:
            path = reverse(page.name, kwargs=dict(page.kwargs or {}))
            absolute_url = urljoin(base_url + "/", path.lstrip("/"))
            lines.extend(
                [
                    "  <url>",
                    f"    <loc>{absolute_url}</loc>",
                    f"    <changefreq>{page.changefreq}</changefreq>",
                    f"    <priority>{page.priority:.1f}</priority>",
                    "  </url>",
                ]
            )

        lines.append("</urlset>")

        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Sitemap generated at {output_path}"))
