# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, UserProfile

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'bio', 'avatar', 'followers_count', 
                 'following_count', 'posts_count']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return UserProfile.objects.filter(followers=obj.user).count()

    def get_posts_count(self, obj):
        return Post.objects.filter(author=obj.user, is_active=True).count()

class CommentSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at', 'likes_count']
        read_only_fields = ['author', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

class CommentDetailSerializer(CommentSerializer):
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ['post']

class PostSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image', 'created_at', 
                 'likes_count', 'comments_count']
        read_only_fields = ['author', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

class PostDetailSerializer(PostSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments'] 