from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment, Tag, Vote, Badge, UserProfile
from .forms import PostForm, CommentForm

class PostListView(ListView):
    model = Post
    template_name = 'community_blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(status='published')
        
        # Dil filtresi
        language = self.request.GET.get('language')
        if language:
            queryset = queryset.filter(language=language)
        
        # Etiket filtresi
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        # Arama
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()
        
        return queryset.order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:10]
        context['languages'] = Post.LANGUAGE_CHOICES
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'community_blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Görüntülenme sayısını artır
        post.view_count += 1
        post.save(update_fields=['view_count'])
        
        # İlgili gönderileri getir
        context['related_posts'] = Post.objects.filter(
            tags__in=post.tags.all(),
            status='published'
        ).exclude(id=post.id).distinct()[:3]
        
        # Yorum formu
        context['comment_form'] = CommentForm()
        
        # Kullanıcının oyları
        if self.request.user.is_authenticated:
            context['user_votes'] = Vote.objects.filter(
                user=self.request.user,
                post=post
            ).values_list('vote_type', flat=True)
        
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'community_blog/post_form.html'
    success_url = reverse_lazy('community_blog:post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = 'pending'  # AI kontrolü için
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'community_blog/post_form.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('community_blog:post_detail', kwargs={'pk': self.object.pk})

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('community_blog:post_list')

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

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
            messages.success(request, _('Yorumunuz başarıyla eklendi.'))
    return redirect('community_blog:post_detail', pk=post.pk)

@login_required
def vote_post(request, pk, vote_type):
    post = get_object_or_404(Post, pk=pk)
    vote, created = Vote.objects.get_or_create(
        user=request.user,
        post=post,
        defaults={'vote_type': vote_type}
    )
    
    if not created:
        if vote.vote_type != vote_type:
            vote.vote_type = vote_type
            vote.save()
        else:
            vote.delete()
    
    return redirect('community_blog:post_detail', pk=post.pk)

@login_required
def vote_comment(request, pk, vote_type):
    comment = get_object_or_404(Comment, pk=pk)
    vote, created = Vote.objects.get_or_create(
        user=request.user,
        comment=comment,
        defaults={'vote_type': vote_type}
    )
    
    if not created:
        if vote.vote_type != vote_type:
            vote.vote_type = vote_type
            vote.save()
        else:
            vote.delete()
    
    return redirect('community_blog:post_detail', pk=comment.post.pk)

class TagDetailView(DetailView):
    model = Tag
    template_name = 'community_blog/tag_detail.html'
    context_object_name = 'tag'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.get_object()
        context['posts'] = Post.objects.filter(
            tags=tag,
            status='published'
        ).order_by('-published_at')
        return context 