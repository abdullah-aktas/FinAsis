from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from typing import List
from rest_framework import viewsets
from django.shortcuts import render
from ..services.nlp_service import LocalNLPService
from ..services import LocalSTTService
from django.conf import settings
import os
from ..services.grounded_qa_service import GroundedQAService
from ..services.knowledge_service import KnowledgeCrawler
from ..services.ocr_service import OCRService
import io


def _to_wav_mono16(audio_bytes: bytes) -> bytes | None:
    """Girdi sesini (webm/ogg/mp3/…) WAV mono 16-bit 16kHz'e dönüştürmeyi dener.

    pydub + ffmpeg gerektirir. Başarısız olursa None döner.
    """
    try:
        from pydub import AudioSegment  # type: ignore
    except Exception:
        return None
    try:
        seg = AudioSegment.from_file(io.BytesIO(audio_bytes))
        seg = seg.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        out = io.BytesIO()
        seg.export(out, format='wav')
        return out.getvalue()
    except Exception:
        return None
from accounting.services.ai_service import (
    map_text_to_voucher_lines,
    map_ocr_to_voucher_lines,
    create_voucher_from_lines,
)
from finance.accounting.models import Account

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_financial_assistant(request):
    """
    Yerel NLP servisi ile doğal dilde finansal soru-cevap.
    Beklenen veri: {"question": "..."}
    """
    try:
        question = request.data.get('question')
        if not question:
            return Response({'error': 'Soru zorunludur.'}, status=status.HTTP_400_BAD_REQUEST)
        nlp = LocalNLPService()
        result = nlp.respond(request.user, question)
        return Response({'result': result})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voice_recognize(request):
    """
    Ses dosyasını (mono 16-bit PCM WAV) metne çevirir ve NLP ile yorumlar.
    Beklenen: multipart/form-data içinde 'file' alanı.
    Cevap: { text: "...", intent_result: {...} }
    """
    try:
        f = request.FILES.get('file') or request.FILES.get('audio')
        if not f:
            return Response({'error': 'Ses dosyası (file) zorunludur.'}, status=400)

        # Model yolu ayarla: settings.AI_STT_MODEL_PATH veya env VOSK_MODEL_PATH
        model_path = getattr(settings, 'AI_STT_MODEL_PATH', None) or os.getenv('VOSK_MODEL_PATH')
        if not model_path:
            return Response({'error': 'STT model yolu tanımlı değil (AI_STT_MODEL_PATH veya VOSK_MODEL_PATH).'}, status=500)

        stt = LocalSTTService(model_path=model_path)
        original_bytes = f.read()
        try:
            text = stt.transcribe(original_bytes)
        except ValueError:
            # Muhtemelen WAV değil veya format uyumsuz; dönüştürmeyi dene
            converted = _to_wav_mono16(original_bytes)
            if not converted:
                return Response({
                    'error': 'Ses formatı desteklenmiyor. Lütfen mono 16-bit PCM WAV yükleyin veya ffmpeg kurup tekrar deneyin.'
                }, status=415)
            text = stt.transcribe(converted)

        nlp = LocalNLPService()
        intent_result = nlp.respond(request.user, text)
        return Response({'text': text, 'result': intent_result})
    except ValueError as ve:
        return Response({'error': str(ve)}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def qa_grounded(request):
    """Belge/mevzuata dayalı yanıt; sadece indekslenmiş kaynaklardan alıntı yapar."""
    try:
        q = request.data.get('query') or request.data.get('question')
        if not q:
            return Response({'error': 'query zorunludur.'}, status=400)
        index_path = getattr(settings, 'AI_KB_INDEX_PATH', None) or os.getenv('AI_KB_INDEX_PATH') or os.path.join(settings.BASE_DIR, 'media', 'ai_kb', 'index.json')
        svc = GroundedQAService(index_path)
        result = svc.answer(q, top_k=int(request.data.get('k', 3)))
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def kb_ingest_urls(request):
    """Dış URL'leri bilgi tabanına ekle (temel tarayıcı)."""
    try:
        urls = request.data.get('urls')
        if not urls or not isinstance(urls, list):
            return Response({'error': 'urls listesi zorunludur.'}, status=400)
        out_path = getattr(settings, 'AI_KB_INDEX_PATH', None) or os.getenv('AI_KB_INDEX_PATH') or os.path.join(settings.BASE_DIR, 'media', 'ai_kb', 'index.json')
        crawler = KnowledgeCrawler(out_path)
        added = crawler.add_urls(urls)
        return Response({'added': added, 'index_path': out_path})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def kb_ingest_internal(request):
    """Proje içi kılavuz ve dökümanları bilgi tabanına ekler."""
    try:
        base_dir = settings.BASE_DIR
        docs_dir = os.path.join(base_dir, 'src', 'apps', 'ai_assistant', 'docs')
        candidates = [
            ('asistan_genel_kilavuz.md', 'Asistan Genel Kılavuz'),
            ('fis_kesme_kilavuzu.md', 'Fiş Kesme Kılavuzu'),
            ('sesli_komut_kilavuzu.md', 'Sesli Komut Kılavuzu'),
            ('grounded_qa_kilavuzu.md', 'Grounded QA Kılavuzu'),
        ]
        docs: List[dict] = []
        for fname, title in candidates:
            fpath = os.path.join(docs_dir, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                docs.append({'path': fpath, 'title': title, 'content': content})
            except FileNotFoundError:
                continue
        out_path = getattr(settings, 'AI_KB_INDEX_PATH', None) or os.getenv('AI_KB_INDEX_PATH') or os.path.join(settings.BASE_DIR, 'media', 'ai_kb', 'index.json')
        crawler = KnowledgeCrawler(out_path)
        added = crawler.add_local_docs(docs)
        return Response({'added': added, 'index_path': out_path, 'docs_loaded': [d['path'] for d in docs]})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voucher_from_text(request):
    """Serbest metinden TDHP uyumlu fiş taslağı üretir (assistant kısayolu)."""
    company = getattr(request.user, 'company', None)
    text = request.data.get('text')
    if not company or not text:
        return Response({'error': 'Eksik veri (company/text).'}, status=400)
    try:
        mapped = map_text_to_voucher_lines(company, text)
        lines = [{
            'account': l['account'].code,
            'account_name': l['account'].name,
            'description': l['description'],
            'debit': str(l['debit']),
            'credit': str(l['credit']),
        } for l in mapped['lines']]
        return Response({'preview': {
            'text': text,
            'date': mapped['date'],
            'reference': mapped['reference'],
            'total': str(mapped['total']),
            'nature': mapped.get('nature'),
            'rule_id': mapped.get('rule_id'),
            'lines': lines
        }})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voucher_from_voice(request):
    """Ses dosyasından (WAV ya da webm) STT ile metin çıkarıp fiş taslağı üretir."""
    company = getattr(request.user, 'company', None)
    f = request.FILES.get('file') or request.FILES.get('audio')
    if not company or not f:
        return Response({'error': 'Eksik veri (company/file).'}, status=400)
    try:
        model_path = getattr(settings, 'AI_STT_MODEL_PATH', None) or os.getenv('VOSK_MODEL_PATH')
        if not model_path:
            return Response({'error': 'STT model yolu tanımlı değil (AI_STT_MODEL_PATH/VOSK_MODEL_PATH).'}, status=500)
        stt = LocalSTTService(model_path=model_path)
        audio_bytes = f.read()
        try:
            text = stt.transcribe(audio_bytes)
        except ValueError:
            converted = _to_wav_mono16(audio_bytes)
            if not converted:
                return Response({
                    'error': 'Ses formatı desteklenmiyor. Lütfen mono 16-bit PCM WAV yükleyin veya ffmpeg kurup tekrar deneyin.'
                }, status=415)
            text = stt.transcribe(converted)
        mapped = map_text_to_voucher_lines(company, text)
        lines = [{
            'account': l['account'].code,
            'account_name': l['account'].name,
            'description': l['description'],
            'debit': str(l['debit']),
            'credit': str(l['credit']),
        } for l in mapped['lines']]
        return Response({'preview': {
            'text': text,
            'date': mapped['date'],
            'reference': mapped['reference'],
            'total': str(mapped['total']),
            'nature': mapped.get('nature'),
            'rule_id': mapped.get('rule_id'),
            'lines': lines
        }})
    except ValueError as ve:
        return Response({'error': str(ve)}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voucher_from_document(request):
    """Belgeyi OCR ile okuyup fiş taslağı üretir (assistant kısayolu)."""
    company = getattr(request.user, 'company', None)
    f = request.FILES.get('file')
    if not company or not f:
        return Response({'error': 'Eksik veri (company/file).'}, status=400)
    try:
        # OCRService path tabanlı çalışıyor; geçici kaydet
        upload = f
        import uuid
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{upload.name}")
        with open(temp_path, 'wb+') as dest:
            for chunk in upload.chunks():
                dest.write(chunk)
        use_google = getattr(settings, 'USE_GOOGLE_VISION', False)
        ocr_service = OCRService(use_google_vision=use_google)
        ocr_data = ocr_service.process_invoice(temp_path)
        try:
            os.remove(temp_path)
        except Exception:
            pass
        mapped = map_ocr_to_voucher_lines(company, ocr_data)
        lines = [{
            'account': l['account'].code,
            'account_name': l['account'].name,
            'description': l['description'],
            'debit': str(l['debit']),
            'credit': str(l['credit']),
        } for l in mapped['lines']]
        return Response({'preview': {
            'date': mapped['date'],
            'reference': mapped['reference'],
            'total': str(mapped['total']),
            'nature': mapped.get('nature'),
            'rule_id': mapped.get('rule_id'),
            'lines': lines
        }})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voucher_confirm(request):
    """Önizlenen fişi oluşturur (assistant kısayolu)."""
    company = getattr(request.user, 'company', None)
    mapped = request.data.get('mapped')
    if not company or not mapped:
        return Response({'error': 'Eksik veri (company/mapped).'}, status=400)
    try:
        resolved_lines = []
        for l in mapped.get('lines', []):
            code = l.get('account')
            if not code:
                return Response({'error': 'Hesap kodu eksik.'}, status=400)
            try:
                acc = Account.objects.get(company=company, code=code)
            except Account.DoesNotExist:
                return Response({'error': f"Hesap bulunamadı: {code}"}, status=400)
            from decimal import Decimal
            resolved_lines.append({
                'account': acc,
                'description': l.get('description', ''),
                'debit': Decimal(str(l.get('debit', '0'))),
                'credit': Decimal(str(l.get('credit', '0'))),
            })
        mapped_resolved = {
            'date': mapped.get('date'),
            'reference': mapped.get('reference'),
            'lines': resolved_lines,
            'total': mapped.get('total'),
        }
        voucher = create_voucher_from_lines(company, mapped_resolved)
        return Response({'status': 'created', 'voucher_id': getattr(voucher, 'id', None)}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

class MyViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({"message": "AI Assistant API çalışıyor."})

def finance_home(request):
    return render(request, "finance/finance_home.html") 