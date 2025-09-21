from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsTeacherOfCourseOrReadOnly(BasePermission):
    """
    Allow writes only if the request.user is the teacher of the related course.
    Read operations allowed to authenticated users with access enforced at queryset level.
    """

    def has_object_permission(self, request, view, obj):
        # Always allow safe methods; visibility handled by queryset scoping per view
        if request.method in SAFE_METHODS:
            return True

        # Identify course for different object types
        course = None
        if hasattr(obj, 'course'):
            course = getattr(obj, 'course', None)
        elif hasattr(obj, 'exam') and hasattr(obj.exam, 'course'):
            course = obj.exam.course
        elif hasattr(obj, 'lesson') and hasattr(obj.lesson, 'course'):
            course = obj.lesson.course

        if course is None:
            return False

        return getattr(course, 'teacher_id', None) == getattr(request.user, 'id', None)
