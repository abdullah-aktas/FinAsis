# -*- coding: utf-8 -*-
"""
Yerel LLM Servisi
Ollama ve Transformers tabanlı yerel AI model desteği
Tamamen yerli çözüm - veriler Türkiye'de kalır
"""
import logging
import os
import json
from typing import Dict, Any, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class LocalLLMService:
    """
    Yerel LLM servisi - Ollama ve Transformers desteği
    Veriler tamamen yerel işlenir, dış servise gönderilmez
    """

    def __init__(self, provider: str = "ollama", model_name: str = None):
        """
        Args:
            provider: "ollama" veya "transformers"
            model_name: Model adı (örn: "llama3.2", "mistral", "qwen2.5")
        """
        self.provider = provider.lower()
        self.model_name = model_name or self._get_default_model()
        self.client = None
        self.model = None
        self.tokenizer = None
        
        # Ollama varsayılan URL
        self.ollama_base_url = os.getenv(
            "OLLAMA_BASE_URL", 
            "http://localhost:11434"
        )
        
        # Model yolu (transformers için)
        self.model_path = os.getenv(
            "LOCAL_LLM_MODEL_PATH",
            os.path.join(settings.BASE_DIR, "models", "llm")
        )
        
        self._initialize()

    def _get_default_model(self) -> str:
        """Varsayılan model adını döndür"""
        # Türkçe destekli modeller öncelikli
        default_models = {
            "ollama": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
            "transformers": os.getenv("TRANSFORMERS_MODEL", "Qwen/Qwen2.5-3B-Instruct"),
        }
        return default_models.get(self.provider, "llama3.2:3b")

    def _initialize(self):
        """Servisi başlat"""
        try:
            if self.provider == "ollama":
                self._init_ollama()
            elif self.provider == "transformers":
                self._init_transformers()
            else:
                logger.warning(f"Bilinmeyen provider: {self.provider}")
        except Exception as e:
            logger.error(f"LLM servisi başlatılamadı: {e}")
            self.client = None
            self.model = None

    def _init_ollama(self):
        """Ollama servisini başlat"""
        try:
            import requests
            self.client = requests
            
            # Ollama'nın çalışıp çalışmadığını kontrol et
            try:
                response = self.client.get(f"{self.ollama_base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info(f"Ollama servisi bağlandı: {self.ollama_base_url}")
                else:
                    logger.warning(f"Ollama servisi yanıt vermiyor: {response.status_code}")
                    self.client = None
            except Exception as e:
                logger.warning(f"Ollama servisine bağlanılamadı: {e}")
                logger.info("Ollama kurulumu için: https://ollama.ai/download")
                self.client = None
        except ImportError:
            logger.warning("requests paketi bulunamadı. Ollama kullanılamayacak.")
            self.client = None

    def _init_transformers(self):
        """Transformers servisini başlat"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            # GPU kontrolü
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Transformers device: {device}")
            
            # Model yolu kontrolü
            if not os.path.exists(self.model_path):
                logger.warning(f"Model yolu bulunamadı: {self.model_path}")
                logger.info("Model indirmek için: python manage.py download_llm_model")
                self.model = None
                return
            
            # Tokenizer yükle
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            # Model yükle
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
            )
            
            if device == "cpu":
                self.model = self.model.to(device)
            
            logger.info(f"Transformers modeli yüklendi: {self.model_name}")
            
        except ImportError:
            logger.warning("transformers paketi bulunamadı. Transformers kullanılamayacak.")
            self.model = None
        except Exception as e:
            logger.error(f"Transformers modeli yüklenemedi: {e}")
            self.model = None

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> str:
        """
        Metin üretir
        
        Args:
            prompt: Kullanıcı mesajı
            system_prompt: Sistem mesajı
            max_tokens: Maksimum token sayısı
            temperature: Yaratıcılık (0.0-1.0)
            top_p: Nucleus sampling
            
        Returns:
            Üretilen metin
        """
        if self.provider == "ollama":
            return self._generate_ollama(prompt, system_prompt, max_tokens, temperature, top_p)
        elif self.provider == "transformers":
            return self._generate_transformers(prompt, system_prompt, max_tokens, temperature, top_p)
        else:
            return "[HATA] LLM servisi başlatılamadı."

    def _generate_ollama(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float
    ) -> str:
        """Ollama ile metin üret"""
        if not self.client:
            return "[HATA] Ollama servisi bağlantısı yok. Lütfen Ollama'yı başlatın."
        
        try:
            # Mesaj formatı
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Ollama API çağrısı
            response = self.client.post(
                f"{self.ollama_base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "options": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": max_tokens,
                    },
                    "stream": False,
                },
                timeout=120,  # 2 dakika timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                logger.error(f"Ollama API hatası: {response.status_code} - {response.text}")
                return f"[HATA] Ollama API hatası: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Ollama generate hatası: {e}")
            return f"[HATA] Ollama generate hatası: {str(e)}"

    def _generate_transformers(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float
    ) -> str:
        """Transformers ile metin üret"""
        if not self.model or not self.tokenizer:
            return "[HATA] Transformers modeli yüklenemedi."
        
        try:
            import torch
            
            # Prompt oluştur
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            # Tokenize
            inputs = self.tokenizer(
                full_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048,
            )
            
            # Device'a taşı
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decode
            generated_text = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            
            return generated_text.strip()
            
        except Exception as e:
            logger.error(f"Transformers generate hatası: {e}")
            return f"[HATA] Transformers generate hatası: {str(e)}"

    def is_available(self) -> bool:
        """Servisin kullanılabilir olup olmadığını kontrol et"""
        if self.provider == "ollama":
            return self.client is not None
        elif self.provider == "transformers":
            return self.model is not None and self.tokenizer is not None
        return False

    def get_model_info(self) -> Dict[str, Any]:
        """Model bilgilerini döndür"""
        return {
            "provider": self.provider,
            "model_name": self.model_name,
            "available": self.is_available(),
            "ollama_url": self.ollama_base_url if self.provider == "ollama" else None,
            "model_path": self.model_path if self.provider == "transformers" else None,
        }

    @staticmethod
    def list_available_models() -> List[Dict[str, str]]:
        """Kullanılabilir Türkçe modelleri listele"""
        return [
            {
                "name": "llama3.2:3b",
                "provider": "ollama",
                "size": "3B",
                "description": "Llama 3.2 3B - Hızlı ve verimli, Türkçe destekli",
                "command": "ollama pull llama3.2:3b",
            },
            {
                "name": "llama3.2:1b",
                "provider": "ollama",
                "size": "1B",
                "description": "Llama 3.2 1B - Çok hızlı, düşük kaynak",
                "command": "ollama pull llama3.2:1b",
            },
            {
                "name": "mistral:7b",
                "provider": "ollama",
                "size": "7B",
                "description": "Mistral 7B - Güçlü performans, Türkçe destekli",
                "command": "ollama pull mistral:7b",
            },
            {
                "name": "qwen2.5:7b",
                "provider": "ollama",
                "size": "7B",
                "description": "Qwen 2.5 7B - Mükemmel Türkçe desteği",
                "command": "ollama pull qwen2.5:7b",
            },
            {
                "name": "Qwen/Qwen2.5-3B-Instruct",
                "provider": "transformers",
                "size": "3B",
                "description": "Qwen 2.5 3B Instruct - Hugging Face, Türkçe destekli",
                "command": "python manage.py download_llm_model Qwen/Qwen2.5-3B-Instruct",
            },
        ]

