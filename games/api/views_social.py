"""
Sosyal özellikler API endpoint'leri
Arkadaş ekleme, takım oluşturma vb.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth import get_user_model
from games.models import Friend, Team, TeamMembership

User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_friend_request(request):
    """Arkadaşlık isteği gönder"""
    username = request.data.get("username")
    if not username:
        return Response(
            {"error": "Kullanıcı adı gereklidir."}, status=status.HTTP_400_BAD_REQUEST
        )

    if username == request.user.username:
        return Response(
            {"error": "Kendinize arkadaşlık isteği gönderemezsiniz."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        to_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND
        )

    # Zaten arkadaş mı kontrol et
    existing = Friend.objects.filter(
        Q(from_player=request.user, to_player=to_user)
        | Q(from_player=to_user, to_player=request.user)
    ).first()

    if existing:
        if existing.status == "accepted":
            return Response(
                {"error": "Bu kullanıcı zaten arkadaşınız."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif existing.status == "pending" and existing.from_player == request.user:
            return Response(
                {"error": "Bu kullanıcıya zaten arkadaşlık isteği gönderdiniz."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif existing.status == "pending" and existing.to_player == request.user:
            # Karşılıklı istek varsa otomatik kabul et
            existing.status = "accepted"
            existing.save()
            return Response(
                {"message": "Arkadaşlık isteği kabul edildi.", "status": "accepted"},
                status=status.HTTP_200_OK,
            )

    # Yeni istek oluştur
    friend_request, created = Friend.objects.get_or_create(
        from_player=request.user, to_player=to_user, defaults={"status": "pending"}
    )

    if not created:
        return Response(
            {"error": "İstek zaten mevcut."}, status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {"message": "Arkadaşlık isteği gönderildi.", "status": "pending"},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_friend_request(request):
    """Arkadaşlık isteğini kabul et"""
    request_id = request.data.get("request_id")
    if not request_id:
        return Response(
            {"error": "İstek ID gereklidir."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        friend_request = Friend.objects.get(
            id=request_id, to_player=request.user, status="pending"
        )
        friend_request.status = "accepted"
        friend_request.save()
        return Response(
            {"message": "Arkadaşlık isteği kabul edildi."}, status=status.HTTP_200_OK
        )
    except Friend.DoesNotExist:
        return Response(
            {"error": "İstek bulunamadı."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_friend_request(request):
    """Arkadaşlık isteğini reddet"""
    request_id = request.data.get("request_id")
    if not request_id:
        return Response(
            {"error": "İstek ID gereklidir."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        friend_request = Friend.objects.get(
            id=request_id, to_player=request.user, status="pending"
        )
        friend_request.delete()
        return Response(
            {"message": "Arkadaşlık isteği reddedildi."}, status=status.HTTP_200_OK
        )
    except Friend.DoesNotExist:
        return Response(
            {"error": "İstek bulunamadı."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_friend(request):
    """Arkadaşı listeden kaldır"""
    username = request.data.get("username")
    if not username:
        return Response(
            {"error": "Kullanıcı adı gereklidir."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        to_user = User.objects.get(username=username)
        friendship = Friend.objects.filter(
            Q(from_player=request.user, to_player=to_user, status="accepted")
            | Q(from_player=to_user, to_player=request.user, status="accepted")
        ).first()

        if friendship:
            friendship.delete()
            return Response(
                {"message": "Arkadaş listeden kaldırıldı."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Arkadaşlık bulunamadı."}, status=status.HTTP_404_NOT_FOUND
            )
    except User.DoesNotExist:
        return Response(
            {"error": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Kullanıcı ara (arkadaş ekleme için)"""
    query = request.query_params.get("q", "")
    if len(query) < 2:
        return Response(
            {"error": "En az 2 karakter girmelisiniz."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)[
        :20
    ]

    # Mevcut arkadaşlık durumlarını kontrol et
    results = []
    for user in users:
        friendship = Friend.objects.filter(
            Q(from_player=request.user, to_player=user)
            | Q(from_player=user, to_player=request.user)
        ).first()

        status_value = None
        if friendship:
            status_value = friendship.status

        results.append(
            {
                "id": user.id,
                "username": user.username,
                "friendship_status": status_value,
            }
        )

    return Response({"users": results})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_team(request):
    """Yeni takım oluştur"""
    name = request.data.get("name")
    tag = request.data.get("tag")
    description = request.data.get("description", "")

    if not name or not tag:
        return Response(
            {"error": "Takım adı ve etiket gereklidir."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Tag 10 karakterden uzun olamaz
    if len(tag) > 10:
        return Response(
            {"error": "Takım etiketi en fazla 10 karakter olabilir."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Aynı isim veya tag var mı kontrol et
    if Team.objects.filter(name=name).exists():
        return Response(
            {"error": "Bu takım adı zaten kullanılıyor."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if Team.objects.filter(tag=tag).exists():
        return Response(
            {"error": "Bu takım etiketi zaten kullanılıyor."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Takım oluştur
    team = Team.objects.create(
        name=name, tag=tag, description=description, owner=request.user
    )

    # Sahibi takıma ekle
    TeamMembership.objects.create(team=team, player=request.user, role="owner")

    return Response(
        {
            "message": "Takım oluşturuldu.",
            "team": {
                "id": team.id,
                "name": team.name,
                "tag": team.tag,
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_team(request):
    """Takıma katıl"""
    team_id = request.data.get("team_id")
    if not team_id:
        return Response(
            {"error": "Takım ID gereklidir."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        team = Team.objects.get(id=team_id)

        # Zaten üye mi kontrol et
        if TeamMembership.objects.filter(team=team, player=request.user).exists():
            return Response(
                {"error": "Zaten bu takımın üyesisiniz."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Üye ekle
        TeamMembership.objects.create(team=team, player=request.user, role="member")

        return Response({"message": "Takıma katıldınız."}, status=status.HTTP_200_OK)
    except Team.DoesNotExist:
        return Response(
            {"error": "Takım bulunamadı."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def leave_team(request):
    """Takımdan ayrıl"""
    team_id = request.data.get("team_id")
    if not team_id:
        return Response(
            {"error": "Takım ID gereklidir."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        team = Team.objects.get(id=team_id)
        membership = TeamMembership.objects.filter(
            team=team, player=request.user
        ).first()

        if not membership:
            return Response(
                {"error": "Bu takımın üyesi değilsiniz."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Sahip takımdan ayrılamaz (önce sahipliği devretmesi gerekir)
        if membership.role == "owner":
            return Response(
                {
                    "error": "Takım sahibi takımdan ayrılamaz. Önce sahipliği devretmelisiniz."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership.delete()
        return Response({"message": "Takımdan ayrıldınız."}, status=status.HTTP_200_OK)
    except Team.DoesNotExist:
        return Response(
            {"error": "Takım bulunamadı."}, status=status.HTTP_404_NOT_FOUND
        )
