from .models import StudentAnalytics
from django.utils import timezone

class AdaptiveLearningService:
    """
    Öğrencinin zayıf olduğu konulara göre kişiselleştirilmiş öneriler sunar.
    """
    def get_recommendations(self, student):
        # Son analitik kaydını al
        analytics = StudentAnalytics.objects.filter(student=student).order_by('-date').first()
        if not analytics or not analytics.weak_topics:
            return {'recommendations': [], 'message': 'Tebrikler! Zayıf konunuz bulunmuyor.'}
        # Zayıf konulara göre öneriler üret
        recommendations = []
        for topic in analytics.weak_topics:
            recommendations.append({
                'topic': topic,
                'suggestion': f"'{topic}' konusunda ek alıştırmalar çözebilir veya öğretmeninizden yardım isteyebilirsiniz."
            })
        return {
            'recommendations': recommendations,
            'message': 'Aşağıdaki konularda gelişim gösterebilirsiniz.'
        } 