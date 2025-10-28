from django.db import models
from django.contrib.auth.models import User
import json


# ===========================
# USER PROFILE MODEL
# ===========================
class UserProfile(models.Model):
    """Extended user information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True, verbose_name='Tên hiển thị')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, verbose_name='Tiểu sử')
    is_online = models.BooleanField(default=False, verbose_name='Trực tuyến')
    last_seen = models.DateTimeField(auto_now=True, verbose_name='Lần cuối trực tuyến')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật lần cuối')
    
    # Game statistics
    total_games_played = models.IntegerField(default=0, verbose_name='Tổng số trận đã chơi')
    total_games_won = models.IntegerField(default=0, verbose_name='Tổng số trận thắng')
    total_messages_sent = models.IntegerField(default=0, verbose_name='Tổng số tin nhắn đã gửi')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_online']),
            models.Index(fields=['-last_seen']),
        ]
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Danh sách hồ sơ người dùng"
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    @property
    def win_rate(self):
        """Calculate win rate percentage"""
        if self.total_games_played == 0:
            return 0
        return round((self.total_games_won / self.total_games_played) * 100, 1)
    
    @property
    def name(self):
        """Get display name or username"""
        return self.display_name or self.user.username
    
    def update_game_stats(self, won=False):
        """Update game statistics"""
        self.total_games_played += 1
        if won:
            self.total_games_won += 1
        self.save()
    
    def update_message_count(self):
        """Update message count"""
        self.total_messages_sent += 1
        self.save()


# ===========================
# CHAT MODELS  
# ===========================
class PrivateChat(models.Model):
    """Private chat between two users"""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user2') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Chat settings
    is_active = models.BooleanField(default=True)
    is_blocked_by_user1 = models.BooleanField(default=False)
    is_blocked_by_user2 = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user1', 'user2']
        indexes = [
            models.Index(fields=['user1', 'user2']),
            models.Index(fields=['-updated_at']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = "Cuộc hội thoại riêng"
        verbose_name_plural = "Danh sách hội thoại riêng"
    
    def __str__(self):
        return f'Chat: {self.user1.username} - {self.user2.username}'
    
    @property
    def chat_id(self):
        """Unique identifier for this chat"""
        # Ensure consistent ordering for chat ID
        ids = sorted([self.user1.id, self.user2.id])
        return f"chat_{ids[0]}_{ids[1]}"
    
    @classmethod
    def get_or_create_chat(cls, user1, user2):
        """Get or create private chat between two users"""
        # Ensure user1.id < user2.id for consistent ordering
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        chat, created = cls.objects.get_or_create(
            user1=user1,
            user2=user2
        )
        return chat, created
    
    @classmethod
    def get_user_chats(cls, user):
        """Get all active chats for a user"""
        return cls.objects.filter(
            models.Q(user1=user) | models.Q(user2=user),
            is_active=True
        ).order_by('-updated_at')
    
    def get_other_user(self, current_user):
        """Get the other user in this chat"""
        return self.user2 if self.user1 == current_user else self.user1
    
    def get_latest_message(self):
        """Get the latest message in this chat"""
        return self.messages.order_by('-timestamp').first()
    
    def get_unread_count(self, user):
        """Get unread message count for user"""
        # Filter messages NOT sent by the user (sent by the other person)
        return self.messages.filter(
            is_read=False
        ).exclude(sender=user).count()
    
    def is_blocked_by(self, user):
        """Check if chat is blocked by user"""
        if user == self.user1:
            return self.is_blocked_by_user1
        elif user == self.user2:
            return self.is_blocked_by_user2
        return False
    
    def block_chat(self, user):
        """Block chat by user"""
        if user == self.user1:
            self.is_blocked_by_user1 = True
        elif user == self.user2:
            self.is_blocked_by_user2 = True
        self.save()
    
    def unblock_chat(self, user):
        """Unblock chat by user"""
        if user == self.user1:
            self.is_blocked_by_user1 = False
        elif user == self.user2:
            self.is_blocked_by_user2 = False
        self.save()


class PrivateMessage(models.Model):
    """Private message between two users"""
    chat = models.ForeignKey(PrivateChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Message types
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System Message'),
    ]
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    
    # File attachment (if any)
    attachment = models.FileField(upload_to='chat_files/', blank=True, null=True)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['chat', '-timestamp']),
            models.Index(fields=['sender', '-timestamp']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return f'{self.sender.username}: {self.content[:50]}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update chat's updated_at when new message is sent
        self.chat.save()
        # Update sender's message count
        if hasattr(self.sender, 'profile'):
            self.sender.profile.update_message_count()
    
    def mark_as_read(self):
        """Mark message as read"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def get_recipient(self):
        """Get message recipient"""
        return self.chat.get_other_user(self.sender)


# ===========================
# LEGACY MODELS (for backward compatibility)
# ===========================
class Room(models.Model):
    """Legacy room model - deprecated"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]


class Message(models.Model):
    """Legacy message model - deprecated"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['room', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
