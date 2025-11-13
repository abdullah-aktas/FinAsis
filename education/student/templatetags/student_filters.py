# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter(name="status_color")
def status_color(status: str) -> str:
    """Map assignment/progress status to Bootstrap color names."""
    if not status:
        return "secondary"
    mapping = {
        # StudentAssignment statuses
        "not_started": "secondary",
        "in_progress": "info",
        "completed": "primary",
        "submitted": "warning",
        "graded": "success",
        # StudentProgress statuses
        "active": "primary",
        "passed": "success",
        "failed": "danger",
        "incomplete": "warning",
    }
    return mapping.get(str(status), "secondary")


@register.filter(name="grade_color")
def grade_color(grade) -> str:
    """Map numeric grade to Bootstrap color names."""
    try:
        val = float(grade)
    except Exception:
        return "secondary"

    if val >= 85:
        return "success"
    if val >= 70:
        return "primary"
    if val >= 50:
        return "warning"
    return "danger"
