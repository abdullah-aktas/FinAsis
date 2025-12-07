# -*- coding: utf-8 -*-
"""
Help System Views
Kullanıcı yardım merkezi
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .help_content import (
    HELP_CONTENT,
    QUICK_TIPS,
    KEYBOARD_SHORTCUTS,
    FAQ_CATEGORIES,
    GUIDED_TOURS,
    TOOLTIPS,
    VIDEO_TUTORIALS,
    ONBOARDING_CHECKLIST,
)


@login_required
def help_center(request):
    """
    Ana yardım merkezi - Kullanıcının rolüne göre ilgili modülleri gösterir
    """
    from accounts.views_panel import _get_user_role_tags
    from accounts.views_panel import _get_user_modules

    # Kullanıcının rolleri
    user_roles = _get_user_role_tags(request.user)

    # Kullanıcının erişebileceği modüller (gerçek modül erişim kontrolü)
    user_modules = _get_user_modules(request.user)
    user_module_keys = [
        m["name"]
        .lower()
        .replace(" ", "_")
        .replace("yapay_zeka", "ai_assistant")
        .replace("finansal_yönetim", "finance")
        .replace("mali_müşavirlik", "advisors")
        .replace("yönetim", "management")
        for m in user_modules
    ]

    # Tüm modülleri rol bazlı filtreleme ile göster
    accessible_modules = []
    for module_key, module_data in HELP_CONTENT.items():
        # Modül erişim kontrolü - kullanıcının gerçek modül erişimi varsa göster
        # Veya admin ise tüm modülleri göster
        if (
            request.user.is_staff
            or request.user.is_superuser
            or module_key in user_module_keys
            or module_key == "accounts"
        ):  # Profil herkese açık
            accessible_modules.append(
                {
                    "key": module_key,
                    "title": module_data["title"],
                    "icon": module_data["icon"],
                    "sections_count": len(module_data.get("sections", [])),
                    "tips_count": len(module_data.get("quick_tips", [])),
                    "description": module_data.get("description", ""),
                }
            )

    context = {
        "title": "Yardım Merkezi",
        "modules": accessible_modules,
        "quick_tips_count": sum(len(tips) for tips in QUICK_TIPS.values()),
        "faq_count": sum(len(cat["questions"]) for cat in FAQ_CATEGORIES.values()),
        "video_count": sum(len(videos) for videos in VIDEO_TUTORIALS.values()),
        "user_roles": user_roles,
    }

    return render(request, "common/help/help_center.html", context)


@login_required
def help_module(request, module_name):
    """
    Modül bazlı yardım sayfası
    """
    if module_name not in HELP_CONTENT:
        return render(
            request,
            "common/help/help_404.html",
            {"message": f'"{module_name}" modülü için yardım içeriği bulunamadı.'},
            status=404,
        )

    module_data = HELP_CONTENT[module_name]

    # Video tutorials
    videos = VIDEO_TUTORIALS.get(module_name, [])

    # Related tips
    tips = module_data.get("quick_tips", [])

    # Shortcuts
    shortcuts = []
    if module_name in KEYBOARD_SHORTCUTS:
        shortcuts = KEYBOARD_SHORTCUTS[module_name]

    context = {
        "title": module_data["title"],
        "module_name": module_name,
        "sections": module_data.get("sections", []),
        "tips": tips,
        "shortcuts": shortcuts,
        "videos": videos,
    }

    return render(request, "common/help/help_module.html", context)


@login_required
def help_faq(request):
    """
    SSS (Sık Sorulan Sorular) sayfası
    """
    # Arama query'si
    search_query = request.GET.get("q", "").strip().lower()

    categories = FAQ_CATEGORIES

    # Arama varsa filtrele
    if search_query:
        filtered_categories = {}
        for cat_key, cat_data in categories.items():
            matching_questions = []
            for q in cat_data["questions"]:
                if (
                    search_query in q["question"].lower()
                    or search_query in q["answer"].lower()
                    or any(search_query in tag for tag in q.get("tags", []))
                ):
                    matching_questions.append(q)

            if matching_questions:
                filtered_categories[cat_key] = {
                    **cat_data,
                    "questions": matching_questions,
                }

        categories = filtered_categories

    total_questions = sum(len(cat["questions"]) for cat in categories.values())

    context = {
        "title": "Sık Sorulan Sorular",
        "categories": categories,
        "search_query": search_query,
        "total_questions": total_questions,
    }

    return render(request, "common/help/help_faq.html", context)


@login_required
def help_videos(request):
    """
    Video eğitimler sayfası
    """
    # Tüm kategorilerdeki videoları topla
    all_videos = []
    for category, videos in VIDEO_TUTORIALS.items():
        for video in videos:
            all_videos.append(
                {
                    **video,
                    "category": category,
                    "category_display": HELP_CONTENT.get(category, {}).get(
                        "title", category
                    ),
                }
            )

    # Seviyeye göre filtrele (opsiyonel)
    level_filter = request.GET.get("level", "")
    if level_filter:
        all_videos = [v for v in all_videos if v["level"] == level_filter]

    context = {
        "title": "Video Eğitimler",
        "videos": all_videos,
        "total_duration": sum(
            int(v["duration"].split(":")[0]) * 60 + int(v["duration"].split(":")[1])
            for v in all_videos
        ),
        "level_filter": level_filter,
    }

    return render(request, "common/help/help_videos.html", context)


@login_required
def help_shortcuts(request):
    """
    Klavye kısayolları sayfası
    """
    context = {
        "title": "Klavye Kısayolları",
        "shortcuts": KEYBOARD_SHORTCUTS,
    }

    return render(request, "common/help/help_shortcuts.html", context)


@login_required
def help_search(request):
    """
    Yardım arama API
    """
    query = request.GET.get("q", "").strip().lower()

    if not query:
        return JsonResponse({"results": []})

    results = []

    # Help content'te ara
    for module_key, module_data in HELP_CONTENT.items():
        if query in module_data["title"].lower():
            results.append(
                {
                    "type": "module",
                    "title": module_data["title"],
                    "url": f"/help/module/{module_key}/",
                    "icon": module_data["icon"],
                }
            )

        for section in module_data.get("sections", []):
            if query in section["title"].lower() or query in section["content"].lower():
                results.append(
                    {
                        "type": "section",
                        "title": section["title"],
                        "module": module_data["title"],
                        "url": f'/help/module/{module_key}/#section-{section["title"]}',
                        "icon": module_data["icon"],
                    }
                )

    # FAQ'te ara
    for cat_key, cat_data in FAQ_CATEGORIES.items():
        for q in cat_data["questions"]:
            if query in q["question"].lower() or query in q["answer"].lower():
                results.append(
                    {
                        "type": "faq",
                        "title": q["question"],
                        "answer_preview": q["answer"][:100] + "...",
                        "url": f"/help/faq/?q={query}",
                        "icon": "bi-question-circle",
                    }
                )

    # Video'larda ara
    for cat_key, videos in VIDEO_TUTORIALS.items():
        for video in videos:
            if query in video["title"].lower() or query in video["description"].lower():
                results.append(
                    {
                        "type": "video",
                        "title": video["title"],
                        "duration": video["duration"],
                        "url": f"/help/videos/#video-{cat_key}",
                        "icon": "bi-play-circle",
                    }
                )

    # İlk 10 sonucu döndür
    return JsonResponse({"results": results[:10]})


@require_GET
def help_api_tooltip(request, tooltip_key):
    """
    Tooltip içeriği API
    """
    tooltip_text = TOOLTIPS.get(tooltip_key, "")
    return JsonResponse({"success": True, "tooltip": tooltip_text})


@require_GET
def help_api_tour(request, tour_name):
    """
    Guided tour verileri API
    """
    tour = GUIDED_TOURS.get(tour_name, None)

    if not tour:
        return JsonResponse({"success": False, "error": "Tour not found"}, status=404)

    return JsonResponse({"success": True, "tour": tour})


@login_required
def help_quick_start(request):
    """
    Hızlı başlangıç rehberi - Rol bazlı özelleştirilmiş
    """
    from accounts.views_panel import _get_user_role_tags

    # Kullanıcının rolleri
    user_roles = _get_user_role_tags(request.user)

    # Onboarding checklist'i al - rol bazlı
    base_checklist = ONBOARDING_CHECKLIST["new_user"].copy()

    # Rol bazlı özelleştirme
    checklist_items = base_checklist.copy()

    # Rol bazlı ek adımlar
    if "teacher" in user_roles or "egitimci" in user_roles:
        checklist_items.append(
            {
                "id": "create_course",
                "title": "İlk dersinizi oluşturun",
                "completed": False,
            }
        )

    if "financial_advisor" in user_roles or "mali_musavir" in user_roles:
        checklist_items.append(
            {"id": "add_client", "title": "İlk müşterinizi ekleyin", "completed": False}
        )

    if request.user.is_staff or request.user.is_superuser:
        checklist_items.append(
            {
                "id": "system_settings",
                "title": "Sistem ayarlarını yapılandırın",
                "completed": False,
            }
        )

    # Kullanıcının tamamladığı adımları işaretle
    user_profile = getattr(request.user, "profile", None)
    if user_profile:
        if hasattr(user_profile, "is_complete") and user_profile.is_complete:
            for item in checklist_items:
                if item["id"] == "profile":
                    item["completed"] = True

    # Şirket bilgisi varsa
    if hasattr(request.user, "company") and request.user.company:
        for item in checklist_items:
            if item["id"] == "company":
                item["completed"] = True

    # İlk fatura kontrolü
    try:
        from accounting.models import Invoice

        if Invoice.objects.filter(created_by=request.user).exists():
            for item in checklist_items:
                if item["id"] == "first_invoice":
                    item["completed"] = True
    except (AttributeError, ImportError, Exception):
        pass

    # İlk ders kontrolü (öğretmenler için)
    if "teacher" in user_roles:
        try:
            from education.models import Course

            if Course.objects.filter(created_by=request.user).exists():
                for item in checklist_items:
                    if item["id"] == "create_course":
                        item["completed"] = True
        except (AttributeError, ImportError, Exception):
            pass

    # İlk müşteri kontrolü (mali müşavirler için)
    if "financial_advisor" in user_roles:
        try:
            advisor_profile = getattr(request.user, "advisor_profile", None)
            if advisor_profile:
                # Müşteri kontrolü için advisors modülüne bakılabilir
                pass
        except:
            pass

    completion_percentage = (
        (
            sum(1 for item in checklist_items if item.get("completed", False))
            / len(checklist_items)
            * 100
        )
        if checklist_items
        else 0
    )

    context = {
        "title": "Hızlı Başlangıç",
        "checklist": checklist_items,
        "completion_percentage": completion_percentage,
        "user_roles": user_roles,
    }

    return render(request, "common/help/help_quick_start.html", context)


@login_required
def help_contact_support(request):
    """
    Destek iletişim formu
    """
    if request.method == "POST":
        # Destek talebi oluştur
        from common.models import SupportTicket

        subject = request.POST.get("subject")
        message = request.POST.get("message")
        priority = request.POST.get("priority", "normal")

        ticket = SupportTicket.objects.create(
            user=request.user,
            subject=subject,
            message=message,
            priority=priority,
            status="open",
        )

        # Email bildirimi gönder (opsiyonel)
        # send_support_ticket_email(ticket)

        return JsonResponse(
            {
                "success": True,
                "ticket_id": ticket.id,
                "message": "Destek talebiniz oluşturuldu. En kısa sürede dönüş yapacağız.",
            }
        )

    context = {
        "title": "Destek Talebi Oluştur",
    }

    return render(request, "common/help/help_contact.html", context)
