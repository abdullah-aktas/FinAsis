from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.conf import settings
from .models import UserProfile, Post, Comment, Tag, Notification, Report
from .forms import PostForm, CommentForm, UserProfileForm
from .tasks import send_notification_email
import json

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'social/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        cache_key = f'posts_{self.request.user.id}_{self.request.GET.get("page", 1)}'
        posts = cache.get(cache_key)
        
        if not posts:
            posts = Post.objects.filter(
                is_active=True
            ).select_related(
                'author'
            ).prefetch_related(
                'likes',
                'comments',
                'tags'
            ).order_by('-created_at')
            
            cache.set(cache_key, posts, timeout=300)
        
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'social/post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        post = super().get_object()
        post.increment_view_count()
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author').order_by('created_at')
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'social/post_form.html'
    success_url = reverse_lazy('social:post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        # Bildirim gönder
        send_notification_email.delay(
            self.object.id,
            'new_post',
            self.request.user.id
        )
        
        return response

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'social/post_form.html'
    success_url = reverse_lazy('social:post_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.is_edited = True
        return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('social:post_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _('Gönderi başarıyla silindi.'))
        return response

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
        
        # Bildirim oluştur
        Notification.objects.create(
            recipient=post.author,
            sender=request.user,
            notification_type='like',
            post=post
        )
    
    return JsonResponse({
        'is_liked': is_liked,
        'like_count': post.get_like_count()
    })

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
            
            # Bildirim oluştur
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='comment',
                post=post,
                comment=comment
            )
            
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.username,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
    
    return JsonResponse({'success': False})

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    profile = user_to_follow.profile
    
    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
        is_following = False
    else:
        profile.followers.add(request.user)
        is_following = True
        
        # Bildirim oluştur
        Notification.objects.create(
            recipient=user_to_follow,
            sender=request.user,
            notification_type='follow'
        )
    
    return JsonResponse({
        'is_following': is_following,
        'follower_count': profile.get_follower_count()
    })

@login_required
def report_content(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        report_type = data.get('report_type')
        content_id = data.get('content_id')
        content_type = data.get('content_type')
        description = data.get('description')
        
        if content_type == 'post':
            content = get_object_or_404(Post, pk=content_id)
        else:
            content = get_object_or_404(Comment, pk=content_id)
        
        Report.objects.create(
            reporter=request.user,
            post=content if content_type == 'post' else None,
            comment=content if content_type == 'comment' else None,
            report_type=report_type,
            description=description
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:10]
    
    data = [{
        'id': n.id,
        'type': n.notification_type,
        'sender': n.sender.username,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for n in notifications]
    
    return JsonResponse({'notifications': data})

class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'social/user_profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(UserProfile, user__username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(
            author=self.object.user,
            is_active=True
        ).order_by('-created_at')
        return context

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'social/user_profile_form.html'
    success_url = reverse_lazy('social:user_profile')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, _('Profil başarıyla güncellendi.'))
        return super().form_valid(form) 