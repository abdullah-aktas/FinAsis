from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.shortcuts import render
from ..services.nlp_service import LocalNLPService

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

class MyViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({"message": "AI Assistant API çalışıyor."})

def finance_home(request):
    return render(request, "finance/finance_home.html") 