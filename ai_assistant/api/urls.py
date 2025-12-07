from django.urls import path
from .views import (
    ask_financial_assistant,
    voice_recognize,
    qa_grounded,
    kb_ingest_urls,
    kb_ingest_internal,
    voucher_from_text,
    voucher_from_voice,
    voucher_from_document,
    voucher_confirm,
)

urlpatterns = [
    path("ask/", ask_financial_assistant, name="ask_financial_assistant"),
    path("voice/recognize/", voice_recognize, name="ai_assistant_voice_recognize"),
    path("qa/grounded/", qa_grounded, name="ai_assistant_qa_grounded"),
    path("kb/ingest-urls/", kb_ingest_urls, name="ai_assistant_kb_ingest_urls"),
    path(
        "kb/ingest-internal/",
        kb_ingest_internal,
        name="ai_assistant_kb_ingest_internal",
    ),
    # Voucher creation shortcuts (AI Assistant wrappers over accounting services)
    path(
        "voucher/from-text/", voucher_from_text, name="ai_assistant_voucher_from_text"
    ),
    path(
        "voucher/from-voice/",
        voucher_from_voice,
        name="ai_assistant_voucher_from_voice",
    ),
    path(
        "voucher/from-document/",
        voucher_from_document,
        name="ai_assistant_voucher_from_document",
    ),
    path("voucher/confirm/", voucher_confirm, name="ai_assistant_voucher_confirm"),
]
