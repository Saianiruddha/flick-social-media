from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Comment, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Enhanced admin configuration for Post model"""
    
    list_display = ('id', 'user', 'caption_preview', 'image_thumbnail', 'likes_count', 'comments_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'caption', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'comments_count')
    list_editable = ('is_active',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Post Information', {
            'fields': ('user', 'caption', 'image')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('likes_count', 'comments_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def caption_preview(self, obj):
        """Show preview of caption"""
        if obj.caption:
            return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
        return '(No caption)'
    caption_preview.short_description = 'Caption'
    
    def image_thumbnail(self, obj):
        """Show image thumbnail"""
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '(No image)'
    image_thumbnail.short_description = 'Image'
    
    def likes_count(self, obj):
        """Show likes count"""
        return obj.total_likes()
    likes_count.short_description = 'Likes'
    
    def comments_count(self, obj):
        """Show comments count"""
        return obj.comments.filter(is_active=True).count()
    comments_count.short_description = 'Comments'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user').prefetch_related('likes', 'comments')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for Comment model"""
    
    list_display = ('id', 'user', 'post_preview', 'content_preview', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'content', 'post__caption')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    list_per_page = 50
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def post_preview(self, obj):
        """Show post preview"""
        caption = obj.post.caption[:30] + '...' if len(obj.post.caption) > 30 else obj.post.caption
        return f"{obj.post.user.username}: {caption}" if caption else f"{obj.post.user.username} (image post)"
    post_preview.short_description = 'Post'
    
    def content_preview(self, obj):
        """Show comment content preview"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user', 'post', 'post__user')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Admin configuration for Follow model"""
    
    list_display = ('id', 'follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    readonly_fields = ('created_at',)
    list_per_page = 50
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('follower', 'following')
