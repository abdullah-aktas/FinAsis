# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import json

SAFE_DIRS = [
    os.path.join(settings.BASE_DIR, 'src', 'apps', 'ai_assistant', 'README.MIGRATION.md'),
    os.path.join(settings.BASE_DIR, 'src', 'apps', 'core_ui', 'README.md'),
    os.path.join(settings.BASE_DIR, 'src', 'apps', 'accounting', 'templates', 'accounting', 'README.MIGRATION.md'),
    os.path.join(settings.BASE_DIR, 'FinAsis', 'docs'),
]

OUT_PATH = os.path.join(settings.BASE_DIR, 'var', 'ai_knowledge.json')


def iter_safe_files():
    for p in SAFE_DIRS:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for fn in files:
                    if fn.lower().endswith(('.md', '.txt', '.csv')):
                        yield os.path.join(root, fn)
        elif os.path.isfile(p):
            yield p


class Command(BaseCommand):
    help = 'Builds a lightweight searchable knowledge index for AI assistant (non-sensitive only).'

    def handle(self, *args, **options):
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        chunks = []
        idx = 0
        for path in iter_safe_files():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                title = os.path.basename(path)
                # Basit chunking: ~2k karakterlik parçalara böl
                step = 2000
                for i in range(0, len(text), step):
                    part = text[i:i+step]
                    chunks.append({
                        'id': f'{idx}',
                        'path': os.path.relpath(path, settings.BASE_DIR),
                        'title': title,
                        'content': part,
                    })
                    idx += 1
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"Skip {path}: {e}"))

        with open(OUT_PATH, 'w', encoding='utf-8') as f:
            json.dump({'chunks': chunks}, f, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"Knowledge index built with {len(chunks)} chunks at {OUT_PATH}"))
