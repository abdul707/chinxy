from django.urls import path
from mainapp import views
from django.views.static import serve

urlpatterns = [
    path('', views.index, name='index'),

    path('login/', views.login, name='login'),

    path('register/', views.signup, name='register'),

    path('logout/', views.logout, name='logout'),

    path('likeUser/', views.likeUser, name='likeUser'),

    path('checkuser/', views.checkuser, name='checkuser'),

    path('profile/', views.userProfile, name='profile'),

    path('editprofile/', views.editprofile, name='editprofile'),

    path('matches/', views.matches, name='matches'),

    path('getCommonHobbies/', views.getCommonHobbies, name='getCommonHobbies'),
]
