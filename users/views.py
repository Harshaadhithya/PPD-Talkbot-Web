from django.shortcuts import render

# Create your views here.
import re
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import custom_user_creation_form,edit_account_form
from .models import Profile


#     profiles,search_query=search_profile(request)

#     context2,profiles=paginate_profiles(request,profiles)

#     context={'profiles':profiles,'search_query':search_query,
#              'page_num_range':context2['page_num_range'],'current_page_num':context2['current_page_num'],
#              'is_having_previous_page':context2['is_having_previous_page'],'is_having_next_page':context2['is_having_next_page'],
#              'previous_page_number':context2['previous_page_number'],'next_page_number':context2['next_page_number'],
#              'is_having_other_pages':context2['is_having_other_pages'],'custom_page_num_range':context2['custom_page_num_range'],
#              'last_page_num':context2['last_page_num'],'last_page_num_minus_1':context2['last_page_num_minus_1']
#              }
#     return render(request,'users/profiles.html',context)

def home(request):
    return render(request,'main.html')


@login_required(login_url='login')
def chat(request):
    return render(request,'users/chat.html')


def user_profile(request,pk):
    profile=Profile.objects.get(id=pk)
    top_skills=profile.skill_set.exclude(description__exact="")
    other_skills=profile.skill_set.filter(description="")
    context={'profile':profile,'top_skills':top_skills,'other_skills':other_skills}
    return render(request,'users/user-profile.html',context)

def login_user(request):
    if request.user.is_authenticated:
        return redirect('profiles') 

    if request.method=='POST':
        entered_username=request.POST['username']
        entered_password=request.POST['password']
        try:
            user=User.objects.get(username=entered_username)
        except:
            messages.error(request,'Username does not exists')
        user=authenticate(request,username=entered_username,password=entered_password)

        if user is not None:
            login(request,user)
            return redirect('my-account')
        else:
            messages.error(request,'Username or Password is incorrect')

    page='login'
    context={'page':page}
    return render(request,'users/login_signup.html',context)

def logout_user(request):
    logout(request)
    messages.success(request,'User was logged out!')
    return redirect('login')

def signup(request):
    page='signup'
    form=custom_user_creation_form()
    if request.method=='POST':
        form=custom_user_creation_form(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            messages.success(request,'User was created successfully')
            login(request,user)
            return redirect('edit-account')
        else:
            messages.error(request,'something went wrong')

            
    context={'page':page,'form':form}
    return render(request,'users/login_signup.html',context)

@login_required(login_url='login')
def my_account(request):
    my_profile=request.user.profile
    # skills=my_profile.skill_set.all()
    # projects=my_profile.project_set.all()
    context={'my_profile':my_profile}
    return render(request,'users/account.html',context)

@login_required(login_url='login')
def edit_account(request):
    profile_data=request.user.profile
    form=edit_account_form(instance=profile_data)
    if request.method=='POST':
        form=edit_account_form(request.POST,request.FILES,instance=profile_data)
        if form.is_valid():
            form.save()
            return redirect('my-account')
    context={'form':form}
    return render(request,'users/edit_my_account.html',context)

