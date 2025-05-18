from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import openai
import os

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_financial_assistant(request):
    """
    OpenAI ile doğal dilde finansal soru-cevap.
    Beklenen veri: {"question": "..."}
    """
    try:
        question = request.data.get('question')
        if not question:
            return Response({'error': 'Soru zorunludur.'}, status=status.HTTP_400_BAD_REQUEST)
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        if not openai.api_key:
            return Response({'error': 'OpenAI API anahtarı tanımlı değil.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen bir finans asistanısın. Kısa, net ve Türkçe cevap ver."},
                {"role": "user", "content": question}
            ],
            max_tokens=256,
            temperature=0.2
        )
        answer = response.choices[0].message.content.strip() if response.choices and response.choices[0].message and response.choices[0].message.content else ""
        return Response({'answer': answer})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 