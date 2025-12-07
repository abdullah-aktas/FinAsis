# -*- coding: utf-8 -*-
from io import BytesIO
from django.http import HttpResponse

try:
    import openpyxl
    from openpyxl.styles import Font
except Exception:  # pragma: no cover
    openpyxl = None
    Font = None  # type: ignore


def export_audit_trails_to_excel(queryset, filename="audit_trails.xlsx"):
    if openpyxl is None:  # openpyxl missing
        return HttpResponse("openpyxl not installed", status=500)

    # Narrow types for type checkers
    wb = openpyxl.Workbook()  # type: ignore[attr-defined]
    ws = wb.active
    # Guard worksheet before using attributes
    if ws is None:
        return HttpResponse("worksheet init failed", status=500)
    ws.title = "Audit Trails"

    headers = ["Timestamp", "Action", "User", "Object", "Description", "IP"]
    if hasattr(ws, "append"):
        ws.append(headers)
        # Bold first row if Font available
        if Font is not None:
            for cell in ws[1]:
                cell.font = Font(bold=True)  # type: ignore[misc]

    for trail in queryset:
        user_name = ""
        user = getattr(trail, "user", None)
        if user is not None:
            full_name = getattr(user, "get_full_name", None)
            if callable(full_name):
                user_name = full_name()
            else:
                user_name = getattr(user, "username", "")
        row = [
            getattr(trail, "timestamp", ""),
            getattr(trail, "action_type", ""),
            user_name,
            str(getattr(trail, "object_repr", getattr(trail, "record_id", ""))),
            getattr(trail, "description", ""),
            getattr(trail, "ip_address", ""),
        ]
        if hasattr(ws, "append"):
            ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
