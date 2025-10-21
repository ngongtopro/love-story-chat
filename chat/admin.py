from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, PrivateChat, PrivateMessage, Room, Message
from caro_game.models import CaroGame


# ===========================
# USER PROFILE ADMIN
# ===========================
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = BaseUserAdmin.list_display + ('is_online', 'total_games', 'win_rate')
    
    def is_online(self, obj):
        return obj.profile.is_online if hasattr(obj, 'profile') else False
    is_online.boolean = True
    is_online.short_description = 'Trực tuyến'
    
    def total_games(self, obj):
        return obj.profile.total_games_played if hasattr(obj, 'profile') else 0
    total_games.short_description = 'Số trận'
    
    def win_rate(self, obj):
        return f"{obj.profile.win_rate}%" if hasattr(obj, 'profile') else "0%"
    win_rate.short_description = 'Tỷ lệ thắng'


# Unregister the default UserAdmin and register our custom UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'is_online', 'total_games_played', 'total_games_won', 'win_rate', 'last_seen')
    list_filter = ('is_online', 'created_at', 'last_seen')
    search_fields = ('user__username', 'display_name', 'bio')
    readonly_fields = ('created_at', 'updated_at', 'last_seen', 'total_games_played', 'total_games_won', 'total_messages_sent')
    
    fieldsets = (
        ('Thông tin người dùng', {
            'fields': ('user', 'display_name', 'avatar', 'bio')
        }),
        ('Trang thái', {
            'fields': ('is_online', 'last_seen')
        }),
        ('Thống kê', {
            'fields': ('total_games_played', 'total_games_won', 'total_messages_sent'),
            'classes': ('collapse',)
        }),
        ('Dấu thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ===========================
# CHAT ADMIN
# ===========================
@admin.register(PrivateChat)
class PrivateChatAdmin(admin.ModelAdmin):
    list_display = ('chat_display', 'is_active', 'message_count', 'latest_message', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at', 'is_blocked_by_user1', 'is_blocked_by_user2')
    search_fields = ('user1__username', 'user2__username')
    readonly_fields = ('chat_id', 'created_at', 'updated_at')
    
    def chat_display(self, obj):
        return f"{obj.user1.username} ↔ {obj.user2.username}"
    chat_display.short_description = 'Chat'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'
    
    def latest_message(self, obj):
        latest = obj.get_latest_message()
        if latest:
            return f"{latest.sender.username}: {latest.content[:30]}..."
        return "No messages"
    latest_message.short_description = 'Latest Message'
    
    fieldsets = (
        ('Chat Info', {
            'fields': ('user1', 'user2', 'chat_id', 'is_active')
        }),
        ('Block Settings', {
            'fields': ('is_blocked_by_user1', 'is_blocked_by_user2'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chat_display', 'content_preview', 'message_type', 'is_read', 'timestamp')
    list_filter = ('message_type', 'is_read', 'timestamp')
    search_fields = ('content', 'sender__username', 'chat__user1__username', 'chat__user2__username')
    readonly_fields = ('timestamp', 'read_at')
    
    def chat_display(self, obj):
        return f"{obj.chat.user1.username} ↔ {obj.chat.user2.username}"
    chat_display.short_description = 'Chat'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    fieldsets = (
        ('Message Info', {
            'fields': ('chat', 'sender', 'content', 'message_type', 'attachment')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )




# ===========================
# LEGACY MODELS ADMIN
# ===========================
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Add warning in changelist
        return qs


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'content_preview', 'timestamp')
    list_filter = ('timestamp', 'room')
    search_fields = ('content', 'user__username', 'room__name')
    readonly_fields = ('timestamp',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'