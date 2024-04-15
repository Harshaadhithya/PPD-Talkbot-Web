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
from openai import OpenAI
from dotenv import load_dotenv
import os
import pyttsx3
from pathlib import Path
from django.conf import settings

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tempfile import NamedTemporaryFile
import os


load_dotenv()


# client.api_key = os.environ.get("OPENAI_KEY")
fine_tuned_model_id = os.environ.get("fine_tuned_model")
client = OpenAI(
    api_key = os.environ.get("OPENAI_KEY")
)



SYSTEM_PROMPT_FOR_PPD_AID = """
You are an very kind hearted and friendly doctor or expert who deals with patients with PPD (Postpartum depression) named Chatner who just loves to aid people with PPD, clear their doubts regarding PPD, and you give them advice and things to follow to overcome and avoid PPD, and you should give mental support for PPD patients. Remember not to mention any personal details or patient names. And Remember that you're like a counselor, so you shgould give them all the support and clarify their doubt, your response should be like you are the expert. Ask them to consult a doctor only if the symptoms are really severe.
Ask Follow up questions if needed to clarify their doubt more efficiently. but don't fail to answer to their response for your follow up question. Your response should give clear solution for their concern. ask follow up questions only when needed.
You should make them feel like they are talking to a human counselor/doctor, so ask questions whenever needed but also provide clear solution for their question.
Don't answer anything that is not releated to PPD/Health, in that case your response should be like, "sorry I am not supposed to answer this question".
"""


def home(request):
    return render(request,'main.html')

def generate_prompt(system_message, user_message, chat_session):
    prompt = []
    old_chat_messages = chat_session.chat_messages.all()
    old_convos=[]
    for chat_message in old_chat_messages:
        if chat_message.messager_type == 'bot':
            old_convos.append({"role": "assistant", "content": chat_message.message})
        else:
            old_convos.append({"role": "user", "content": chat_message.message})
    prompt.append({"role": "system", "content": system_message})
    prompt.extend(old_convos)
    prompt.append({"role": "user", "content":f"Here is the latest user question, before that keep in mind that you shouldn't answer anything that is not releated to PPD/Health, in that case your response should be like, 'sorry I am not supposed to answer this question': If the question is related to PPD/Health then answer to this like an medical expert specialised in PPD, make use of the old conversation between you and the patient and answer the last user question like an caring counselor. Based on the previous conversation, if it seems too severe then along with your response, add somthing like 'Its always best to consult a health professional'. here is the question: <question>{user_message}</question>"})
    print(prompt)
    return prompt

def generate_prompt_for_chat_session_title(user_message):
    prompt = []
    prompt.append({"role": "system", "content": "you should act like an expert in drafting very short headings and it should be clear and short."})
    user_content = f"Below is the message i am using to starting a convo with a chatbot, based on my below message generate a apt heading for that:\n {user_message}"
    prompt.append({"role": "user", "content":user_content})
    return prompt


@login_required(login_url='login')
def record_feedback_up(request, pk):
    chat_message = ChatMessage.objects.get(id=pk)
    chat_message.feedback = 'helpful'
    chat_message.save()
    return redirect('chat', pk=chat_message.chat_session.id)

@login_required(login_url='login')
def record_feedback_down(request, pk):
    chat_message = ChatMessage.objects.get(id=pk)
    chat_message.feedback = 'not_helpful'
    chat_message.save()
    return redirect('chat', pk=chat_message.chat_session.id)


from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
import base64
from pydub import AudioSegment
import io

@login_required(login_url='login')
def process_audio(request, pk):
    chat_session = ChatSession.objects.get(id=pk)
    newly_created_id = None
    print("files", request.FILES)
    print("post", request.POST)
    if request.method == 'POST' and 'audio' in request.POST:
        print("coming in")
        audio_base64 = request.POST['audio'].split(',')[1]  # Extract the base64-encoded audio data
        
        # Decode the base64 data
        audio_bytes = base64.b64decode(audio_base64)
        
        # Create a Django ContentFile object from the decoded audio bytes
        audio_file = ContentFile(audio_bytes)
        
        # Convert the audio file to a supported format (e.g., WAV)
        audio = AudioSegment.from_file(audio_file)
        temp_output_file = NamedTemporaryFile(delete=False, suffix='.wav')
        audio.export(temp_output_file.name, format='wav')
        


        # Read the contents of the temporary file as bytes
        with open(temp_output_file.name, 'rb') as file_content:
            audio_content = file_content.read()

            # Call the OpenAI API to generate text from the audio file
            try:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=temp_output_file
                )
                transcription_text = transcription.text
            finally:
                # Clean up the temporary audio file
                os.unlink(temp_output_file.name)
        message = transcription_text
        user_chat_message = ChatMessage.objects.create(chat_session=chat_session, messager_type='user', message=message)
        chat_session = ChatSession.objects.get(id=pk)
        if len(chat_session.chat_messages.all())==1:
            print("inside...")
            #generate chat title
            generate_heading_prompt = generate_prompt_for_chat_session_title(user_message=message)
            heading_response = client.chat.completions.create(
                model=fine_tuned_model_id,
                messages=generate_heading_prompt,
                temperature=0,
                max_tokens=800
            )
            heading = heading_response.choices[0].message.content
            print('heading',heading)
            chat_session.chat_subject = heading
            chat_session.save()
        
        # openai code here
        prompt = generate_prompt(system_message=SYSTEM_PROMPT_FOR_PPD_AID, user_message=message, chat_session = chat_session)
        response = client.chat.completions.create(
            model=fine_tuned_model_id,
            messages=prompt,
            temperature=0,
            max_tokens=800
        )
        bot_response_message = response.choices[0].message.content
        
        # engine = pyttsx3.init()
        # engine.say("Hi Navina, I am a text to speech engine. I can convert text to speech.")
        # engine.runAndWait()

        bot_response_chat_message = ChatMessage.objects.create(chat_session=chat_session, messager_type='bot', message=bot_response_message)
        speech_file_path = Path(settings.MEDIA_ROOT) / f"{bot_response_chat_message.id}.mp3"  # Generate unique file name
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=bot_response_message
        )
        print(audio_response)
        audio_response.stream_to_file(speech_file_path)
        bot_response_chat_message.audio.name = str(speech_file_path.relative_to(settings.MEDIA_ROOT))
        print(str(speech_file_path.relative_to(settings.MEDIA_ROOT)), bot_response_chat_message.audio )
        bot_response_chat_message.save()
        print(bot_response_chat_message.id)
        newly_created_id = bot_response_chat_message.id
        
        
    chat_messages = chat_session.chat_messages.all()
    last_message = chat_session.chat_messages.last()
    if chat_messages:
        last_message_id = last_message.id
    else: 
        last_message_id = None
    context={'chat_messages':chat_messages, 'newly_created_id': newly_created_id, 'last_message_id':last_message_id, 'chat_session_id':pk}
    return render(request,'users/new_chat.html', context)
        

@login_required(login_url='login')
def chat(request, pk):
    chat_session = ChatSession.objects.get(id=pk)
    newly_created_id = None
    if request.method=='POST':
        message = request.POST['message']
        user_chat_message = ChatMessage.objects.create(chat_session=chat_session, messager_type='user', message=message)
        chat_session = ChatSession.objects.get(id=pk)
        if len(chat_session.chat_messages.all())==1:
            print("inside...")
            #generate chat title
            generate_heading_prompt = generate_prompt_for_chat_session_title(user_message=message)
            heading_response = client.chat.completions.create(
                model=fine_tuned_model_id,
                messages=generate_heading_prompt,
                temperature=0,
                max_tokens=800
            )
            heading = heading_response.choices[0].message.content
            print('heading',heading)
            chat_session.chat_subject = heading
            chat_session.save()
        
        # openai code here
        prompt = generate_prompt(system_message=SYSTEM_PROMPT_FOR_PPD_AID, user_message=message, chat_session = chat_session)
        response = client.chat.completions.create(
            model=fine_tuned_model_id,
            messages=prompt,
            temperature=0,
            max_tokens=800
        )
        bot_response_message = response.choices[0].message.content
        
       
        bot_response_chat_message = ChatMessage.objects.create(chat_session=chat_session, messager_type='bot', message=bot_response_message, response_to=user_chat_message)
        speech_file_path = Path(settings.MEDIA_ROOT) / f"{bot_response_chat_message.id}.mp3"  # Generate unique file name
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=bot_response_message
        )
        print(audio_response)
        audio_response.stream_to_file(speech_file_path)
        bot_response_chat_message.audio.name = str(speech_file_path.relative_to(settings.MEDIA_ROOT))
        print(str(speech_file_path.relative_to(settings.MEDIA_ROOT)), bot_response_chat_message.audio )
        bot_response_chat_message.save()
        print(bot_response_chat_message.id)
        newly_created_id = bot_response_chat_message.id
        
        
    chat_messages = chat_session.chat_messages.all()
    last_message = chat_session.chat_messages.last()
    if chat_messages:
        last_message_id = last_message.id
    else: 
        last_message_id = None
    context={'chat_messages':chat_messages, 'newly_created_id': newly_created_id, 'last_message_id':last_message_id, 'chat_session_id':pk}
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

