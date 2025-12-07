# -*- coding: utf-8 -*-
import logging
from typing import Dict, Any, List, Optional, cast
from django.contrib.auth.models import User
from ..models import UserInteraction
import os
from django.conf import settings
from .knowledge_service import KnowledgeIndex

# Optional dependency: OpenAI SDK (v1). Guard import to avoid import-time failures.
try:
    from openai import OpenAI  # type: ignore
    from openai.types.chat import ChatCompletionMessageParam  # type: ignore
except Exception:
    OpenAI = None  # will be validated at runtime when service is used
    ChatCompletionMessageParam = Dict[str, Any]  # fallback for typing

logger = logging.getLogger(__name__)


class ChatAIService:
    def __init__(self):
        """AI sohbet servisi başlatıcı"""
        # Mock modu: test/sunucuda anahtar yoksa basit yanıt üret
        self.mock_mode = os.getenv("FINASIS_AI_MOCK", "0") in ("1", "true", "True")
        # API istemcisi varsayılan olarak yok; uygun koşullarda oluşturulacak
        self.client: Optional[Any] = None

        # OpenAI paketi yoksa zorunlu mock moda geç ve uyarı logla
        if OpenAI is None:
            logger.warning(
                "OpenAI paketi bulunamadı; ChatAIService mock modunda çalışacak."
            )
            self.mock_mode = True
            self.api_key = None
        else:
            # API anahtarını al ve uygun ise istemciyi başlat
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                # API anahtarı yoksa mock moda düş
                self.mock_mode = True
            else:
                # Yeni SDK istemcisi
                try:
                    self.client = OpenAI(api_key=self.api_key)
                except Exception as e:
                    logger.error(f"OpenAI istemcisi başlatılırken hata: {e}")
                    self.client = None
                    self.mock_mode = True

        # Sistem rolü: Finansman/Muhasebe uzmanı ve FinAsis bağlam bilgesi
        assistant_name = os.getenv("FINASIS_AI_WIDGET_NAME", "FinAsis Bilgesi")
        default_prompt = (
            f"Sen {assistant_name} — FinAsis platformunun deneyimli bir Yapay Zeka asistanısın. "
            "Tam kapsamlı bir finansman ve muhasebe uzmanı gibi davran: TFRS/IFRS prensipleri, nakit akışı, bütçe, mali tablolar, vergisel esaslar, e-dönüşüm (e-Fatura, e-Defter) ve ERP/LMS entegrasyonları hakkında derin bilgiye sahipsin. "
            "Cevaplarında net, adım adım ve pratik ol; mümkünse kısa madde işaretleri kullan. "
            "FinAsis modüllerini biliyorsun (Muhasebe, AI Asistan, OCR, Tahmin, Oyunlaştırma, Blockchain kanıt vs.) ve kullanıcıyı bu özelliklerle yönlendirebilirsin. "
            "Bilmediğin noktada varsayım yapma, alternatif kaynak/aksiyon öner."
        )
        self.system_prompt = os.getenv("FINASIS_AI_SYSTEM_PROMPT", default_prompt)
        # Bilgi indeksi (varsa yükle)
        try:
            base_dir = (
                getattr(settings, "BASE_DIR", None)
                or os.getenv("FINASIS_BASE_DIR")
                or os.getcwd()
            )
        except Exception:
            base_dir = os.getenv("FINASIS_BASE_DIR") or os.getcwd()
        self.knowledge_path = os.path.join(base_dir, "var", "ai_knowledge.json")
        self.knowledge = KnowledgeIndex.load(self.knowledge_path)

    def get_response(
        self, user: User, query: str, context: Dict[str, Any] | None = None
    ) -> str:
        """
        Kullanıcı sorgusuna yanıt verir

        Args:
            user (User): Kullanıcı nesnesi
            query (str): Kullanıcı sorgusu
            context (dict|None): Opsiyonel sayfa/uygulama bağlamı (path, title, locale vb.)

        Returns:
            str: AI yanıtı
        """
        try:
            # Model adı (env ile override edilebilir)
            model_name = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

            # Son sohbet geçmişini al
            history = UserInteraction.objects.filter(
                user=user, interaction_type="chat"
            ).order_by("-created_at")[:5]

            # Sistem mesajını ve bağlamı hazırla
            system_content = self.system_prompt
            if context:
                try:
                    ctx_bits = []
                    page = context.get("page_path") or context.get("path")
                    title = context.get("page_title") or context.get("title")
                    if page:
                        ctx_bits.append(f"Sayfa: {page}")
                    if title:
                        ctx_bits.append(f"Başlık: {title}")
                    if ctx_bits:
                        system_content += "\nBağlam: " + " | ".join(ctx_bits)
                except Exception:
                    # Bağlam oluşturma hatasını yut, kritik değil
                    pass

            # Rol tabanlı rehberlik
            role_hints = []
            try:
                roles = list(getattr(user, "groups").all().values_list("name", flat=True))  # type: ignore
                if "accountant" in [r.lower() for r in roles]:
                    role_hints.append(
                        "Kullanıcı bir muhasebecidir; kayıt, mutabakat, raporlama odaklı öneriler ver."
                    )
                if "manager" in [r.lower() for r in roles] or user.is_staff:
                    role_hints.append(
                        "Kullanıcı yönetici/karar vericidir; özet ve aksiyon odaklı anlat."
                    )
            except Exception:
                pass
            if role_hints:
                system_content += "\nRol Notları: " + " | ".join(role_hints)

            messages: List[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_content}
            ]

            # Geçmiş mesajları ekle
            for interaction in reversed(history):
                if getattr(interaction, "content", None):
                    messages.append({"role": "user", "content": interaction.content})
                if getattr(interaction, "ai_response", None):
                    messages.append(
                        {"role": "assistant", "content": interaction.ai_response}
                    )

            # Bilgi tabanından ilgili parçaları getir ve kullanıcı mesajına ek bağlam olarak iliştir
            user_content = query
            if self.knowledge and isinstance(query, str):
                tops = self.knowledge.search(
                    query, top_k=int(os.getenv("FINASIS_AI_RETRIEVE_K", "3"))
                )
                if tops:
                    refs = "\n\n[İlgili Bilgi]" + "".join(
                        f"\n- {t.title} ({t.path})\n{t.content[:400]}..." for t in tops
                    )
                    user_content += refs

            # Yeni sorguyu ekle
            messages.append({"role": "user", "content": user_content})

            # Mock yanıt (istemci yoksa da mock'a düş)
            if self.mock_mode or not getattr(self, "client", None):
                prefix = "[MOCK] FinAsis Cevap (Mock)"
                tips = (
                    "• Nakit akışı ve kârlılık metriklerini düzenli takip edin.\n"
                    "• Cari oranı >1.2, Borç/Özsermaye <2 hedefleyin.\n"
                    "• Bütçe-tahmin sapmalarını aylık analiz edin."
                )
                ctx = f"\n[Bağlam: {context}]" if context else ""
                return f"{prefix}: {query[:120]}...\n{tips}{ctx}"

            # OpenAI API'yi çağır (v1 SDK)
            # Bu noktada istemci mevcut olmalı; type checker için cast kullanıyoruz
            client = cast(Any, self.client)
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.4")),
                    max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "800")),
                    timeout=float(os.getenv("OPENAI_REQUEST_TIMEOUT", "20")),
                )

                # Yanıtı al
                ai_response = response.choices[0].message.content or ""  # type: ignore[assignment]
                return ai_response
            except Exception as call_err:
                # Bağlantı/istek hatalarında kullanıcıya yedek cevap dön
                logger.error(f"OpenAI sohbet isteği başarısız: {call_err}")
                prefix = "[FALLBACK] FinAsis Cevap (Yedek Mod)"
                tips = (
                    "• Şu an AI servisine bağlanırken bir sorun oluştu; geçici öneriler sunuluyor.\n"
                    "• Nakit akışı ve kârlılık metriklerini düzenli takip edin.\n"
                    "• Cari oranı >1.2, Borç/Özsermaye <2 hedefleyin.\n"
                    "• Bütçe-tahmin sapmalarını aylık analiz edin."
                )
                ctx = f"\n[Bağlam: {context}]" if context else ""
                return f"{prefix}: {query[:120]}...\n{tips}{ctx}"

        except Exception as e:
            # Genel beklenmeyen hatalarda da yedek cevap dön
            logger.error(f"AI sohbet hatası: {str(e)}")
            prefix = "[FALLBACK] FinAsis Cevap (Yedek Mod)"
            tips = (
                "• Şu an AI servisine bağlanırken bir sorun oluştu; geçici öneriler sunuluyor.\n"
                "• Nakit akışı ve kârlılık metriklerini düzenli takip edin.\n"
                "• Cari oranı >1.2, Borç/Özsermaye <2 hedefleyin.\n"
                "• Bütçe-tahmin sapmalarını aylık analiz edin."
            )
            ctx = f"\n[Bağlam: {context}]" if context else ""
            return f"{prefix}: {query[:120]}...\n{tips}{ctx}"
