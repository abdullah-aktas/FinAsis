"""
Role Assignment API Views
Otomatik rol atama sistemi için REST API endpoint'leri
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from common.auto_role_assignment import (
    assign_roles_to_user,
    bulk_assign_roles,
    get_role_assignment_summary,
    create_required_groups,
    AUTO_ROLE_RULES,
    ADMIN_USER_RULES,
    EMAIL_DOMAIN_RULES
)

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def role_assignment_summary(request):
    """
    Rol atama durumu özetini döndürür
    GET /api/v1/admin/role-assignment/summary/
    """
    try:
        summary = get_role_assignment_summary()
        return Response({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def role_assignment_rules(request):
    """
    Otomatik rol atama kurallarını döndürür
    GET /api/v1/admin/role-assignment/rules/
    """
    return Response({
        'success': True,
        'data': {
            'user_type_rules': AUTO_ROLE_RULES,
            'admin_user_rules': ADMIN_USER_RULES,
            'email_domain_rules': EMAIL_DOMAIN_RULES
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def assign_roles_all_users(request):
    """
    Tüm kullanıcılara rol atar
    POST /api/v1/admin/role-assignment/assign-all/
    Body: {"force": true/false}
    """
    force = request.data.get('force', False)
    
    try:
        result = bulk_assign_roles(force=force)
        return Response({
            'success': True,
            'data': result,
            'message': f'Toplu rol atama tamamlandı! Başarılı: {result["success"]}, Hatalı: {result["errors"]}'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def assign_roles_single_user(request, user_id):
    """
    Belirli bir kullanıcıya rol atar
    POST /api/v1/admin/role-assignment/assign-user/<user_id>/
    Body: {"force": true/false}
    """
    force = request.data.get('force', False)
    
    try:
        user = User.objects.get(id=user_id)
        result = assign_roles_to_user(user, force=force)
        
        if result['success']:
            return Response({
                'success': True,
                'data': result,
                'message': f'{user.username} kullanıcısına rol atama başarılı!'
            })
        else:
            return Response({
                'success': False,
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Kullanıcı bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def assign_roles_by_user_type(request, user_type_code):
    """
    Belirli user_type'a sahip kullanıcılara rol atar
    POST /api/v1/admin/role-assignment/assign-user-type/<user_type_code>/
    Body: {"force": true/false}
    """
    force = request.data.get('force', False)
    
    try:
        users = User.objects.filter(user_type__code=user_type_code)
        
        if not users.exists():
            return Response({
                'success': False,
                'error': f'{user_type_code} user_type\'ına sahip kullanıcı bulunamadı'
            }, status=status.HTTP_404_NOT_FOUND)
        
        result = bulk_assign_roles(users=users, force=force)
        
        return Response({
            'success': True,
            'data': result,
            'message': f'{user_type_code} user_type için rol atama tamamlandı! Başarılı: {result["success"]}, Hatalı: {result["errors"]}'
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_required_groups_api(request):
    """
    Gerekli grupları oluşturur
    POST /api/v1/admin/role-assignment/create-groups/
    """
    try:
        created_count = create_required_groups()
        return Response({
            'success': True,
            'data': {
                'created_count': created_count
            },
            'message': f'{created_count} grup oluşturuldu/kontrol edildi!'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def users_without_groups(request):
    """
    Grup ataması olmayan kullanıcıları listeler
    GET /api/v1/admin/role-assignment/users-without-groups/
    """
    try:
        users = User.objects.filter(groups__isnull=True).select_related('user_type')
        
        user_data = []
        for user in users:
            user_type_obj = getattr(user, 'user_type', None)
            user_data.append({
                'id': getattr(user, 'id', None),
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': getattr(user, 'role', None),
                'user_type': user_type_obj.code if user_type_obj else None,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined
            })
        
        return Response({
            'success': True,
            'data': {
                'count': len(user_data),
                'users': user_data
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def group_statistics(request):
    """
    Grup istatistiklerini döndürür
    GET /api/v1/admin/role-assignment/group-stats/
    """
    try:
        groups_data = []
        for group in Group.objects.all():
            users_in_group = User.objects.filter(groups=group).select_related('user_type')
            
            user_types = {}
            for user in users_in_group:
                user_type_obj = getattr(user, 'user_type', None)
                user_type = user_type_obj.code if user_type_obj else 'unknown'
                user_types[user_type] = user_types.get(user_type, 0) + 1
            
            groups_data.append({
                'name': group.name,
                'user_count': users_in_group.count(),
                'user_types': user_types
            })
        
        return Response({
            'success': True,
            'data': {
                'total_groups': len(groups_data),
                'groups': groups_data
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_role_info(request):
    """
    Kullanıcının kendi rol bilgilerini döndürür
    GET /api/v1/role-assignment/my-info/
    """
    user = request.user
    
    try:
        user_groups = list(user.groups.values_list('name', flat=True))
        user_type_obj = getattr(user, 'user_type', None)
        
        return Response({
            'success': True,
            'data': {
                'user_id': getattr(user, 'id', None),
                'username': user.username,
                'role': getattr(user, 'role', None),
                'groups': user_groups,
                'user_type': user_type_obj.code if user_type_obj else None,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'permissions': list(user.get_all_permissions())
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)