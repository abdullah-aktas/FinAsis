from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .models import ApprovalRequest, AuditLog


@login_required
def request_approval(request, app_label, model, pk):
    try:
        ct = ContentType.objects.get(app_label=app_label, model=model)
    except ContentType.DoesNotExist:
        raise Http404
    obj = get_object_or_404(ct.model_class(), pk=pk)
    ar, created = ApprovalRequest.objects.get_or_create(
        content_type=ct, object_id=str(pk), defaults={"requested_by": request.user}
    )
    AuditLog.log_action(
        obj=obj,
        action="approval_request",
        user=request.user,
        ip=request.META.get("REMOTE_ADDR"),
    )
    return JsonResponse({"status": "ok", "created": created, "approval_id": ar.id})


@login_required
def approval_action(request, pk, action):
    ar = get_object_or_404(ApprovalRequest, pk=pk)
    if action == "approve":
        ar.approve(user=request.user)
        AuditLog.log_action(
            obj=ar.content_object,
            action="approved",
            user=request.user,
            ip=request.META.get("REMOTE_ADDR"),
        )
    elif action == "reject":
        ar.reject(user=request.user)
        AuditLog.log_action(
            obj=ar.content_object,
            action="rejected",
            user=request.user,
            ip=request.META.get("REMOTE_ADDR"),
        )
    else:
        return JsonResponse(
            {"status": "error", "message": "invalid action"}, status=400
        )
    return JsonResponse({"status": "ok", "new_status": ar.status})


@login_required
def audit_list(request):
    qs = AuditLog.objects.all()[:200]
    data = [
        {
            "id": x.id,
            "action": x.action,
            "object": f"{x.content_type.app_label}.{x.content_type.model}:{x.object_id}",
            "user": getattr(x.user, "username", None),
            "created_at": x.created_at.isoformat(),
        }
        for x in qs
    ]
    return JsonResponse({"results": data})
