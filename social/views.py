from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Post, Comment, UserProfile
from .forms import PostForm, CommentForm, UserProfileForm
from .serializers import (
    PostSerializer, CommentSerializer, UserProfileSerializer,
    PostDetailSerializer, CommentDetailSerializer
)

User = get_user_model()

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'social/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by('-created_at')
    comment_form = CommentForm()
    return render(request, 'social/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Gönderi başarıyla oluşturuldu.')
            return redirect('social:post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'social/post_form.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        messages.error(request, 'Bu gönderiyi düzenleme yetkiniz yok.')
        return redirect('social:post_detail', pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gönderi başarıyla güncellendi.')
            return redirect('social:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'social/post_form.html', {'form': form})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        messages.error(request, 'Bu gönderiyi silme yetkiniz yok.')
        return redirect('social:post_detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Gönderi başarıyla silindi.')
        return redirect('social:post_list')
    return render(request, 'social/post_confirm_delete.html', {'post': post})

@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Yorum başarıyla eklendi.')
    return redirect('social:post_detail', pk=pk)

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.author:
        messages.error(request, 'Bu yorumu silme yetkiniz yok.')
        return redirect('social:post_detail', pk=comment.post.pk)
    
    post_pk = comment.post.pk
    comment.delete()
    messages.success(request, 'Yorum başarıyla silindi.')
    return redirect('social:post_detail', pk=post_pk)

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = UserProfile.objects.get_or_create(user=user)[0]
    posts = Post.objects.filter(author=user).order_by('-created_at')
    return render(request, 'social/user_profile.html', {
        'profile': profile,
        'posts': posts
    })

@login_required
def edit_profile(request):
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil başarıyla güncellendi.')
            return redirect('social:user_profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'social/edit_profile.html', {'form': form})

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if request.user != user_to_follow:
        profile = UserProfile.objects.get_or_create(user=request.user)[0]
        if user_to_follow not in profile.following.all():
            profile.following.add(user_to_follow)
            messages.success(request, f'{user_to_follow.username} kullanıcısını takip etmeye başladınız.')
    return redirect('social:user_profile', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    if user_to_unfollow in profile.following.all():
        profile.following.remove(user_to_unfollow)
        messages.success(request, f'{user_to_unfollow.username} kullanıcısını takip etmeyi bıraktınız.')
    return redirect('social:user_profile', username=username)

class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(is_active=True).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()

    def perform_update(self, serializer):
        if serializer.instance.author == self.request.user:
            serializer.save()
        else:
            raise permissions.PermissionDenied("Bu gönderiyi düzenleme yetkiniz yok.")

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("Bu gönderiyi silme yetkiniz yok.")

class PostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            return Response({"status": "unliked"})
        else:
            post.likes.add(request.user)
            return Response({"status": "liked"})

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        serializer.save(author=self.request.user, post=post)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()

    def perform_update(self, serializer):
        if serializer.instance.author == self.request.user:
            serializer.save()
        else:
            raise permissions.PermissionDenied("Bu yorumu düzenleme yetkiniz yok.")

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("Bu yorumu silme yetkiniz yok.")

class CommentLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            return Response({"status": "unliked"})
        else:
            comment.likes.add(request.user)
            return Response({"status": "liked"})

class UserFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user_to_follow = get_object_or_404(User, pk=pk)
        if request.user == user_to_follow:
            return Response(
                {"error": "Kendinizi takip edemezsiniz."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.user in user_to_follow.profile.followers.all():
            return Response(
                {"error": "Bu kullanıcıyı zaten takip ediyorsunuz."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_to_follow.profile.followers.add(request.user)
        return Response({"status": "following"})

class UserUnfollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user_to_unfollow = get_object_or_404(User, pk=pk)
        if request.user not in user_to_unfollow.profile.followers.all():
            return Response(
                {"error": "Bu kullanıcıyı zaten takip etmiyorsunuz."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_to_unfollow.profile.followers.remove(request.user)
        return Response({"status": "unfollowed"})

class UserFollowersView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        return UserProfile.objects.filter(user__in=user.profile.followers.all())

class UserFollowingView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        return UserProfile.objects.filter(followers=user) 