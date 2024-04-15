from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('user-profile/<str:pk>/',views.user_profile,name='user-profile'),

    path('login/',views.login_user,name='login'),
    path('signup/',views.signup,name='signup'),
    path('logout/',views.logout_user,name='logout'),

    path('my-account/',views.my_account,name='my-account'),
    path('edit-account/',views.edit_account,name='edit-account'),

    path('my_chats/', views.my_chats, name='my-chats'),
    path('new_chat', views.new_chat, name='new-chat'),

    path('chat/<str:pk>/', views.chat, name='chat'),
    path('record-feedback-up/<str:pk>/', views.record_feedback_up, name='record-feedback-up'),
    path('record-feedback-down/<str:pk>/', views.record_feedback_down, name='record-feedback-down'),

    # path('process_audio/<str:pk>/', views.process_audio, name='process-audio')
]