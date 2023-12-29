from django.db.models.signals import post_save,post_delete

from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.models import User
from .models import Profile

def user_created_receiver(sender,instance,created,**kwargs):
    if created:
        profile=Profile.objects.create(
            user=instance,
            username=instance.username,
            email=instance.email,
            name=instance.first_name
            )


def profile_delete_receiver(sender,instance,**kwargs):
    try:
        user_record=instance.user
        user_record.delete()
    except:
        pass
    
def profile_update_reciever(sender,instance,created,**kwargs):
    profile=instance
    user=profile.user
    
    if created==False:
        user.username=profile.username
        user.first_name=profile.name
        user.email=profile.email
        user.save()


post_save.connect(user_created_receiver,sender=User)

post_delete.connect(profile_delete_receiver,sender=Profile)

post_save.connect(profile_update_reciever,sender=Profile)
