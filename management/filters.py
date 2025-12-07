import django_filters
from accounts.models import CustomUser


class UserFilter(django_filters.FilterSet):
    date_joined = django_filters.DateFromToRangeFilter(label="Kayıt Tarihi (aralık)")
    is_staff = django_filters.BooleanFilter(label="Yönetici mi?")
    is_superuser = django_filters.BooleanFilter(label="Süper Admin mi?")
    username = django_filters.CharFilter(lookup_expr="icontains", label="Kullanıcı Adı")
    email = django_filters.CharFilter(lookup_expr="icontains", label="E-posta")

    class Meta:
        model = CustomUser
        fields = ["username", "email", "is_staff", "is_superuser", "date_joined"]
