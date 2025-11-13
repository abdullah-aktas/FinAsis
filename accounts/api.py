from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Achievement, UserSettings
from rest_framework import serializers
from accounting.models import Company
from rest_framework import status

class UserProfileSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'company_name', 'role']

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'sector', 'tax_number', 'address', 'phone', 'email', 'logo']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'title', 'description', 'icon', 'date_earned', 'company']

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['email_notifications', 'dark_mode']

class CompanyView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.company:
            serializer = CompanySerializer(request.user.company)
            return Response(serializer.data)
        return Response({'detail': 'Şirket yok.'}, status=status.HTTP_404_NOT_FOUND)

class AchievementsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        achievements = Achievement.objects.filter(company=request.user.company)
        serializer = AchievementSerializer(achievements, many=True)
        return Response(serializer.data)

class UserSettingsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSettingsSerializer(request.user.settings)
        return Response(serializer.data) 