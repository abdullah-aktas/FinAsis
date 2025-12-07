"""
Role Assignment Admin Interface
Otomatik rol atama sistemi için Django admin arayüzü
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from common.auto_role_assignment import (
    assign_roles_to_user,
    bulk_assign_roles,
    get_role_assignment_summary,
    create_required_groups,
)

User = get_user_model()


@staff_member_required
def role_assignment_view(request):
    """Ana rol atama sayfası"""
    summary = get_role_assignment_summary()

    # Son 10 kullanıcıyı göster
    recent_users = (
        User.objects.select_related("user_type")
        .prefetch_related("groups")
        .order_by("-date_joined")[:10]
    )

    # Uyumlu summary yapısı oluştur
    compatible_summary = {
        "total_users": summary["total_users"],
        "total_groups": summary["total_groups"],
        "users_with_roles": summary["users_with_groups"],
        "users_without_roles": summary["users_without_groups"],
        "admin_users": summary.get("admin_users", 0),
        "coverage_percentage": summary["coverage_percentage"],
        "groups": summary["group_stats"],
    }

    context = {
        "title": "Otomatik Rol Atama Yönetimi",
        "summary": compatible_summary,
        "recent_users": recent_users,
        "has_permission": True,
    }

    return render(request, "admin/common/role_assignment.html", context)


@require_POST
@staff_member_required
def assign_all_users(request):
    """Tüm kullanıcılara rol atar (AJAX)"""
    force = request.POST.get("force") == "true"

    try:
        result = bulk_assign_roles(force=force)
        messages.success(
            request,
            f'Toplu rol atama tamamlandı! Başarılı: {result["success"]}, Hatalı: {result["errors"]}',
        )
        return JsonResponse({"success": True, "result": result})
    except Exception as e:
        messages.error(request, f"Toplu rol atama hatası: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
@staff_member_required
def assign_single_user(request, user_id):
    """Belirli bir kullanıcıya rol atar (AJAX)"""
    force = request.POST.get("force") == "true"

    try:
        user = User.objects.get(id=user_id)
        result = assign_roles_to_user(user, force=force)

        if result["success"]:
            messages.success(
                request, f"{user.username} kullanıcısına rol atama başarılı!"
            )
            return JsonResponse({"success": True, "result": result})
        else:
            messages.error(
                request,
                f'{user.username} kullanıcısına rol atama hatası: {result["error"]}',
            )
            return JsonResponse({"success": False, "error": result["error"]})
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Kullanıcı bulunamadı"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
@staff_member_required
def create_groups(request):
    """Gerekli grupları oluşturur (AJAX)"""
    try:
        created_count = create_required_groups()
        messages.success(request, f"{created_count} grup oluşturuldu/kontrol edildi!")
        return JsonResponse({"success": True, "created_count": created_count})
    except Exception as e:
        messages.error(request, f"Grup oluşturma hatası: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)})


# User admin'ini genişlet
class CustomUserAdmin(admin.ModelAdmin):
    """Kullanıcı admin'ine rol atama fonksiyonu ekler"""

    actions = ["assign_roles_to_selected"]

    @admin.action(description="Seçili kullanıcılara otomatik rol ata")
    def assign_roles_to_selected(self, request, queryset):
        """Seçili kullanıcılara rol atar"""
        result = bulk_assign_roles(users=queryset, force=False)

        self.message_user(
            request,
            f'Rol atama tamamlandı! Başarılı: {result["success"]}, Hatalı: {result["errors"]}',
        )


# Admin URL patterns'i oluştur
admin_url_patterns = [
    path("role-assignment/", role_assignment_view, name="role_assignment"),
    path(
        "role-assignment/assign-all/",
        assign_all_users,
        name="role_assignment_assign_all",
    ),
    path(
        "role-assignment/assign-user/<int:user_id>/",
        assign_single_user,
        name="role_assignment_assign_user",
    ),
    path(
        "role-assignment/create-groups/",
        create_groups,
        name="role_assignment_create_groups",
    ),
]
