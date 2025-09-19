from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile


# Extend the built-in UserAdmin
class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('bio', 'profile_image', 'birth_date', 'location', 'website', 'is_private', 'email_notifications')


class CustomUserAdmin(BaseUserAdmin):
    """Extended User admin with profile inline"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'posts_count', 'followers_count')
    list_filter = BaseUserAdmin.list_filter + ('profile__is_private',)
    
    def posts_count(self, obj):
        """Show user's posts count"""
        return obj.posts.filter(is_active=True).count()
    posts_count.short_description = 'Posts'
    
    def followers_count(self, obj):
        """Show user's followers count"""
        return obj.followers.count()
    followers_count.short_description = 'Followers'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('profile').prefetch_related('posts', 'followers')


# Unregister the original User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model"""
    
    list_display = ('user', 'profile_image_thumbnail', 'bio_preview', 'location', 'is_private', 'posts_count', 'followers_count', 'created_at')
    list_filter = ('is_private', 'email_notifications', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    readonly_fields = ('created_at', 'updated_at', 'posts_count', 'followers_count', 'following_count')
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('bio', 'profile_image', 'birth_date', 'location', 'website')
        }),
        ('Privacy Settings', {
            'fields': ('is_private', 'email_notifications')
        }),
        ('Statistics', {
            'fields': ('posts_count', 'followers_count', 'following_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def profile_image_thumbnail(self, obj):
        """Show profile image thumbnail"""
        if obj.profile_image and obj.profile_image.name != 'profiles/default-profile.png':
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />', obj.profile_image.url)
        return '(Default image)'
    profile_image_thumbnail.short_description = 'Profile Image'
    
    def bio_preview(self, obj):
        """Show bio preview"""
        if obj.bio:
            return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
        return '(No bio)'
    bio_preview.short_description = 'Bio'
    
    def posts_count(self, obj):
        """Show user's posts count"""
        return obj.get_posts_count()
    posts_count.short_description = 'Posts'
    
    def followers_count(self, obj):
        """Show user's followers count"""
        return obj.get_followers_count()
    followers_count.short_description = 'Followers'
    
    def following_count(self, obj):
        """Show user's following count"""
        return obj.get_following_count()
    following_count.short_description = 'Following'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user').prefetch_related('user__posts', 'user__followers', 'user__following')
