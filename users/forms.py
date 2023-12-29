from django.db import models
from django.db.models import fields
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class custom_user_creation_form(UserCreationForm):
    class Meta:
        model=User
        fields=['first_name','email','username','password1','password2']
        labels={'first_name':'Name'}

    def __init__(self,*args,**kwargs):
        super(custom_user_creation_form,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs.update({'class':'input'})
        self.fields['email'].widget.attrs.update({'class':'input'})
        self.fields['username'].widget.attrs.update({'class':'input'})
        self.fields['password1'].widget.attrs.update({'class':'input'})
        self.fields['password2'].widget.attrs.update({'class':'input'})

class edit_account_form(ModelForm):
    class Meta:
        model=Profile
        fields= ['name','email','username','profile_image']

    def __init__(self,*args,**kwargs):
        super(edit_account_form,self).__init__(*args,**kwargs)
        self.fields['name'].widget.attrs.update({'class':'input'})
        self.fields['email'].widget.attrs.update({'class':'input'})
        self.fields['username'].widget.attrs.update({'class':'input'})
        # self.fields['bio'].widget.attrs.update({'class':'input'})
        self.fields['profile_image'].widget.attrs.update({'class':'input'})
        
