from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone




class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    name=models.CharField(max_length=200,null=True,blank=True)
    email=models.EmailField(max_length=400,null=True,blank=True)
    username=models.CharField(max_length=200,null=True,blank=True)
    bio=models.TextField(blank=True,null=True)
    profile_image=models.ImageField(null=False,blank=False,upload_to='profiles/',default='profiles/user-default.png')
    created=models.DateTimeField(auto_now_add=True)
    id=models.UUIDField(default=uuid.uuid4,unique=True,primary_key=True,editable=False)

    def __str__(self):
        return str(self.username)

    class Meta:
        ordering=['-created']


class ChatSession(models.Model):
    profile = models.ForeignKey(Profile, on_delete = models.CASCADE)
    chat_subject = models.TextField(null=True, blank=True, default="No Subject")
    created_at = models.DateTimeField(auto_now_add=True)
    id=models.UUIDField(default=uuid.uuid4,unique=True,primary_key=True,editable=False)
    updated_at = models.DateTimeField()

    class Meta:
        ordering = ["-updated_at"]

    @property
    def total_messages(self):
        return len(self.chat_messages.all())

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super(ChatSession, self).save(*args, **kwargs)

class ChatMessage(models.Model):
    messager_type_choices = (
        ('bot', 'bot'),
        ('user', 'user')
    )
    feedback_choices = (
        ('helpful', 'helpful'),
        ('not_helpful', 'not_helpful')
    )
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='chat_messages')
    messager_type = models.CharField(max_length=50, choices=messager_type_choices)
    feedback = models.CharField(max_length=50, choices = feedback_choices, null=True, blank=True)
    response_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='responses')
    message = models.TextField()
    audio = models.FileField(upload_to='audio/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    id=models.UUIDField(default=uuid.uuid4,unique=True,primary_key=True,editable=False)

    class Meta:
        ordering=['created_at']

    def save(self, *args, **kwargs):
        self.chat_session.updated_at = timezone.now()
        self.chat_session.save()
        super().save(*args, **kwargs)


