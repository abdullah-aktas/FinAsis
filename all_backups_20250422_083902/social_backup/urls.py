from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/like/', views.PostLikeView.as_view(), name='post-like'),
    path('posts/<int:pk>/comment/', views.CommentCreateView.as_view(), name='comment-create'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('comments/<int:pk>/like/', views.CommentLikeView.as_view(), name='comment-like'),
    path('users/<int:pk>/follow/', views.UserFollowView.as_view(), name='user-follow'),
    path('users/<int:pk>/unfollow/', views.UserUnfollowView.as_view(), name='user-unfollow'),
    path('users/<int:pk>/followers/', views.UserFollowersView.as_view(), name='user-followers'),
    path('users/<int:pk>/following/', views.UserFollowingView.as_view(), name='user-following'),
] 