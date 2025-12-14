# -*- coding: utf-8 -*-
"""
Yerel LLM modeli indirme komutu
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Yerel LLM modelini Hugging Face'den indirir"

    def add_arguments(self, parser):
        parser.add_argument(
            "model_name",
            type=str,
            nargs="?",
            default="Qwen/Qwen2.5-3B-Instruct",
            help="Hugging Face model adı (örn: Qwen/Qwen2.5-3B-Instruct)",
        )
        parser.add_argument(
            "--provider",
            type=str,
            choices=["transformers", "ollama"],
            default="transformers",
            help="Model provider (transformers veya ollama)",
        )

    def handle(self, *args, **options):
        model_name = options["model_name"]
        provider = options["provider"]

        if provider == "ollama":
            self.stdout.write(
                self.style.WARNING(
                    "Ollama için model indirme komutu: ollama pull <model_name>"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(f"Örnek: ollama pull {model_name.replace(':', ' ')}")
            )
            return

        # Transformers için model indirme
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
        except ImportError:
            self.stdout.write(
                self.style.ERROR(
                    "transformers paketi bulunamadı. Lütfen kurun: pip install transformers torch"
                )
            )
            return

        # Model yolu
        model_path = os.path.join(
            settings.BASE_DIR, "models", "llm", model_name.replace("/", "_")
        )
        os.makedirs(model_path, exist_ok=True)

        self.stdout.write(self.style.SUCCESS(f"Model indiriliyor: {model_name}"))
        self.stdout.write(f"Hedef: {model_path}")

        try:
            # Tokenizer indir
            self.stdout.write("Tokenizer indiriliyor...")
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=model_path,
                trust_remote_code=True,
            )

            # Model indir
            self.stdout.write("Model indiriliyor (bu biraz zaman alabilir)...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16,
            )

            # Modeli kaydet
            tokenizer.save_pretrained(model_path)
            model.save_pretrained(model_path)

            self.stdout.write(
                self.style.SUCCESS(f"✅ Model başarıyla indirildi: {model_path}")
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Environment değişkeni: LOCAL_LLM_MODEL_PATH={model_path}"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Model indirme hatası: {e}"))
