from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, Http404, JsonResponse, QueryDict, HttpResponseRedirect
from django.template import RequestContext, loader
from mainapp.models import Member, Profile, Hobby, Gender
from django.contrib.auth.hashers import make_password
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import json
from .forms import LoginForm, RegisterForm, EditForm
from django.core.mail import send_mail
from django.urls import reverse
import datetime as D

appname = 'Chinxy'
#Passing the app name to the render function which directs to index.html
def index(request):
    context = { 'appname': appname }
    return render(request,'mainapp/index.html',context)
#Using a decorator to check if a user is logged in
def loggedin(view):
    def mod_view(request):
        if 'username' in request.session:
            username = request.session['username']
            try: user = Member.objects.get(username=username)
            except Member.DoesNotExist: raise Http404('Member does not exist')
            return view(request, user)
        else:
            return render(request,'mainapp/invalidlogin.html',{})
    return mod_view
#Here we take the user inputs in order to login
def login(request):
    # Checking if input is a POST
    if request.method == 'POST':
        # Establish a loginForm object which includes the inputs
        form = LoginForm(request.POST)
        # Ensuring the form is valid
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                 member = Member.objects.get(username=username)
            except Member.DoesNotExist:
                raise Http404('User does not exist')
            if member.check_password(password):
                # remember user in session variable
                request.session['username'] = username
                request.session['password'] = password
                context = {
                   'appname': appname,
                   'username': username,
                   'profile': member.profile,
                   'loggedin': True
                }
                response = render(request, 'mainapp/matches.html', context)

                # remember last login in cookie
                now = D.datetime.utcnow()
                max_age = 365 * 24 * 60 * 60
                delta = now + D.timedelta(seconds=max_age)
                format = "%a, %d-%b-%Y %H:%M:%S GMT"
                expires = D.datetime.strftime(delta, format)
                response.set_cookie('last_login',now,expires=expires)

                return response
            else:
                return render(request,'mainapp/invalidpassword.html',{})
    else:
        form = LoginForm()

    return render(request, 'mainapp/login.html', {'form': form})

def signup(request):
    # Testing if the request method is POST if so we continue and
    # create a registration form taking in the user's request
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            #Here we are creating a new profile and storing each field in the database
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            hobbies = form.cleaned_data['hobbies']
            gender = form.cleaned_data['gender']
            dateob = form.cleaned_data['dob']
            image_file = form.cleaned_data['file']
            hobbyList = []
            for hob in hobbies:
                hobby = Hobby.objects.get(pk = hob)
                hobbyList.append(hobby)
            g = Gender.objects.get(pk = gender)
            profile = Profile(image = image_file, dob=dateob)
            profile.save()
            user = Member(username = username,
                         email = email,
                          profile = profile,
                          gender =g
                          )
            user.set_password(password)
            user.save()
            user.hobbies.set(hobbyList)
            return HttpResponseRedirect('/login')
    else:
        form = RegisterForm()

    return render(request, 'mainapp/register.html', {'form': form})

#renders user to editprofile.html page
@loggedin
def editprofilepage(request, user):
    context = { 'appname': appname }
    return render(request,'mainapp/editprofile.html',context)

#Here we are giving the user the functionality to edit their profile
#The current users profile will be updated with the new inputs
#Once they have completed the editing they will be redirected to the profile page
@loggedin
def editprofile(request, user):
    if request.method == 'POST':
        print(user.username)
        form = EditForm(request.POST, request.FILES, data = user)
        if form.is_valid():
            email = form.cleaned_data['email']
            hobbies = form.cleaned_data['hobbies']
            gender = form.cleaned_data['gender']
            if form.cleaned_data['file'] != None:
                image_file = form.cleaned_data['file']
                user.profile.image = image_file
                user.profile.save()
            hobbyList = []
            for hob in hobbies:
                hobby = Hobby.objects.get(pk = hob)
                hobbyList.append(hobby)
            g = Gender.objects.get(pk = gender)
            user.email = email
            user.gender = g
            user.save()
            user.hobbies.set(hobbyList)
            return HttpResponseRedirect('/profile')
    else:
        form = EditForm(data = user)

    context = {
        'appname': appname,
        'username': user.username,
        'profile' : user.profile,
        'loggedin': True,
        'form': form
    }
    return render(request, 'mainapp/editprofile.html', context)

#Relevant information passed down to matches.html
@loggedin
def matches(request, user):
    context = {
        'appname': appname,
        'username': user.username,
        'profile' : user.profile,
        'loggedin': True
    }
    return render(request,'mainapp/matches.html',context)
#User information is passed down in context to the render function which displays the user profile
@loggedin
def userProfile(request,user):
    list = []
    for hobs in user.hobbies.all():
        list.append(hobs.name)
    context = {
        'appname': appname,
        'user': user,
        'profile' : user.profile,
        'loggedin': True,
        'hobbies' : list
    }
    return render(request,'mainapp/profile.html',context)
#Deletes the current session data from the session and deletes the session cookie
@loggedin
def logout(request, user):
    request.session.flush()
    context = { 'appname': appname }
    return render(request,'mainapp/logout.html', context)
# Checks whether the logged in users has liked a member and Orders a list of users
# with the most common hobbies as the logged in user (most at the top least at the bottom)
@loggedin
def getCommonHobbies(request, user):
    likesList = []
    for likes in user.likes.all():
        likesList.append(likes)
    hobbyList = []
    for hobs in user.hobbies.all():
        hobbyList.append(hobs.name)
    json_res = []
    for mem in Member.objects.all():
        if mem != user:
            memberHobbies = []
            for m in mem.hobbies.all():
                memberHobbies.append(m.name)
            sameHobbies = []
            for k in set(hobbyList).intersection(memberHobbies):
                sameHobbies.append(k)
            if mem in user.likes.all():
                json_obj = dict(
                    length = len(set(hobbyList).intersection(memberHobbies)),
                    sameHobbies = sameHobbies,
                    name = mem.username,
                    id = mem.id,
                    gender = mem.gender.name,
                    dob = str(mem.profile.dob),
                    image = mem.profile.image.url,
                    liked = True
                )
            else:
                json_obj = dict(
                    length = len(set(hobbyList).intersection(memberHobbies)),
                    sameHobbies = sameHobbies,
                    name = mem.username,
                    id = mem.id,
                    gender = mem.gender.name,
                    dob = str(mem.profile.dob),
                    image = mem.profile.image.url,
                    liked = False
                )
            json_res.append(json_obj)
    json_res.sort(key=lambda x: x['length'], reverse=True)
    return JsonResponse(json_res, safe=False)
#Sends email notifications when a user likes another profile
@loggedin
def likeUser(request, user):
    if request.method == "POST":
        if 'likeID' in request.POST:
            likeID = request.POST['likeID']
            likesList = []
            for l in user.likes.all():
                likesList.append(l)
            liked = Member.objects.get(pk = likeID)
            likesList.append(liked)
            user.likes.set(likesList)
            send_mail(
                        user.username + ' likes you!',
                        user.username + ' has liked you, login to check em out! <3',
                        str(user.email),
                        [str(liked.email)],
                        fail_silently=False,
                    )
        else:
            dislikeID = request.POST['dislikeID']
            disliked = Member.objects.get(pk = dislikeID)
            likesList = []
            for d in user.likes.all():
                if d != disliked:
                    likesList.append(d)
            user.likes.set(likesList)
            send_mail(
                        user.username + ' stopped liking you! :(',
                         user.username + ' has disliked you, login to your account',
                        str(user.email),
                        [str(disliked.email)],
                        fail_silently=False,
                    )
        return JsonResponse("", safe=False)

#Here we are validating if the username of the person is unique for 'login' and 'register'
def checkuser(request):
    if 'username' in request.POST:
        try:
            member = Member.objects.get(username=request.POST['username'])
        except Member.DoesNotExist:
            if request.POST['page'] == 'login':
                return HttpResponse("<span class='taken'>&nbsp;&#x2718; Invalid username</span>")
            if request.POST['page'] == 'register':
                return HttpResponse("<span class='available'>&nbsp;&#x2714; This username is available</span>")
    if request.POST['page'] == 'login':
        return HttpResponse("<span class='available'>&nbsp;&#x2714; Valid username</span>")
    if request.POST['page'] == 'register':
        return HttpResponse("<span class='taken'>&nbsp;&#x2718; This username is taken</span>")
    return HttpResponse("<span class='taken'>&nbsp;&#x2718; Invalid request</span>")
