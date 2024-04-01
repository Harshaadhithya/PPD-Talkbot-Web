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
from .models import *
import openai
from dotenv import load_dotenv
import os

load_dotenv()


openai.api_key = os.environ.get("OPENAI_KEY")
fine_tuned_model_id = os.environ.get("fine_tuned_model")


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

SYSTEM_PROMPT_FOR_PPD_AID = "You are an very kind hearted and friendly doctor or expert who deals with patients with PPD (Postpartum depression) named Chatner who just loves to aid people with PPD, clear their doubts regarding PPD, and you give them advice and things to follow to overcome and avoid PPD, and you should give mental support for PPD patients."


def home(request):
    return render(request,'main.html')

def generate_prompt(system_message, user_message):
    prompt = []
    prompt.append({"role": "system", "content": system_message})
    prompt.append({"role": "user", "content": user_message})
    return prompt

def generate_prompt_for_chat_session_title(user_message):
    prompt = []
    prompt.append({"role": "system", "content": "you should act like an expert in drafting very short headings and it should be clear and short."})
    user_content = f"Below is the message i am using to starting a convo with a chatbot, based on my below message generate a apt heading for that:\n {user_message}"
    prompt.append({"role": "user", "content":user_content})
    return prompt


@login_required(login_url='login')
def chat(request, pk):
    chat_session = ChatSession.objects.get(id=pk)
    if request.method=='POST':
        message = request.POST['message']
        user_chat_message = ChatMessage.objects.create(chat_session=chat_session, messager_type='user', message=message)
        chat_session = ChatSession.objects.get(id=pk)
        if len(chat_session.chat_messages.all())==1:
            print("inside...")
            #generate chat title
            generate_heading_prompt = generate_prompt_for_chat_session_title(user_message=message)
            heading_response = openai.ChatCompletion.create(
                model=fine_tuned_model_id,
                messages=generate_heading_prompt,
                temperature=0,
                max_tokens=800
            )
            heading = heading_response["choices"][0]["message"]["content"]
            print('heading',heading)
            chat_session.chat_subject = heading
            chat_session.save()
        
        # openai code here
        prompt = generate_prompt(system_message=SYSTEM_PROMPT_FOR_PPD_AID, user_message=message)
        response = openai.ChatCompletion.create(
            model=fine_tuned_model_id,
            messages=prompt,
            temperature=0,
            max_tokens=800
        )
        bot_response_message = response["choices"][0]["message"]["content"]
        bot_response_chat_message = ChatMessage.objects.create(chat_session=chat_session, messager_type='bot', message=bot_response_message )
        
    chat_messages = chat_session.chat_messages.all()
    context={'chat_messages':chat_messages}
    return render(request,'users/new_chat.html', context)

@login_required(login_url='login')
def my_chats(request):
    my_chats = ChatSession.objects.filter(profile = request.user.profile)
    context = {'my_chats':my_chats}
    return render(request, 'users/my_chats.html', context)

@login_required(login_url='login')
def new_chat(request):
    chat_sessions = ChatSession.objects.filter()
    if not chat_sessions.exists():
        chat_session = ChatSession.objects.create(profile = request.user.profile)
    else:
        last_session = chat_sessions.first()
        if last_session.total_messages != 0:
            chat_session = ChatSession.objects.create(profile = request.user.profile)
        else:
            chat_session = last_session
            

    return redirect('chat', pk=chat_session.id)



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

