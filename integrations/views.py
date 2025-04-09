from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import EInvoice, EArchive, BankIntegration
from .services import EInvoiceService, EArchiveService, BankIntegrationService
from .serializers import (
    EInvoiceSerializer, 
    EArchiveSerializer, 
    BankIntegrationSerializer,
    BankTransactionSerializer
)

class EInvoiceViewSet(viewsets.ModelViewSet):
    queryset = EInvoice.objects.all()
    serializer_class = EInvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EInvoice.objects.filter(sender=self.request.user)
    
    def create(self, request, *args, **kwargs):
        service = EInvoiceService()
        try:
            invoice = service.create_invoice(request.data)
            serializer = self.get_serializer(invoice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class EArchiveViewSet(viewsets.ModelViewSet):
    queryset = EArchive.objects.all()
    serializer_class = EArchiveSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EArchive.objects.filter(document_owner=self.request.user)
    
    def create(self, request, *args, **kwargs):
        service = EArchiveService()
        try:
            file = request.FILES.get('file')
            metadata = {
                'type': request.data.get('document_type'),
                'date': request.data.get('document_date'),
                'owner': request.user
            }
            archive = service.archive_document(file, metadata)
            serializer = self.get_serializer(archive)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def ocr_content(self, request, pk=None):
        archive = self.get_object()
        return Response({
            'content': archive.ocr_content
        })

class BankIntegrationViewSet(viewsets.ModelViewSet):
    queryset = BankIntegration.objects.all()
    serializer_class = BankIntegrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BankIntegration.objects.filter(account_holder=self.request.user)
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        integration = self.get_object()
        service = BankIntegrationService(integration)
        try:
            balance = service.get_balance()
            return Response({
                'balance': balance,
                'currency': 'TRY',
                'last_sync': integration.last_sync
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        integration = self.get_object()
        service = BankIntegrationService(integration)
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            transactions = service.get_transactions(start_date, end_date)
            serializer = BankTransactionSerializer(transactions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 