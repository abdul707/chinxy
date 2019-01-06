from django import forms
from django.contrib.admin import widgets
from mainapp.models import Member, Profile, Hobby, Gender
import datetime as D

# This is a login form that will include username and password fields
class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class':'loginusername form-control','placeholder':'Enter Username...','style':'width: 44%; position: relative; box-sizing: border-box; height: auto; padding: 10px; font-size: 15px; border-top-right-radius: 4px; border-bottom-right-radius: 4px;'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter Password...','style':'width: 44%; position: relative; box-sizing: border-box; height: auto; padding: 10px; font-size: 15px; border-top-right-radius: 4px; border-bottom-right-radius: 4px;'}))

# This is a registration form that includes the relevant information needed to create an account
class RegisterForm(forms.Form):
    # All dating sites have an age limit of 18 so we are ensuring that our users are of age
    now = D.datetime.utcnow()
    minAge =D.timedelta(seconds=365 * 24 * 60 * 60 * 17)
    delta = now - minAge
    format = "%Y"
    minage = D.datetime.strftime(delta, format)

    # Here we get all of the hobbies that we have stored in the database
    hobb=Hobby.objects.all()
    hobbyList = []
    for hobs in hobb:
        hobbyList.append((hobs.pk,hobs.name))

    # A list of genders
    genders=Gender.objects.all()
    genderList = []
    for gen in genders:
        genderList.append((gen.pk,gen.name))

    username = forms.CharField(widget=forms.TextInput(attrs={'class':'registerusername form-control','placeholder':'Enter Username...'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter Password...'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter Email Address...'}))
    gender = forms.ChoiceField(choices=genderList,widget=forms.Select(attrs={'class': 'Gender form-control'}))
    dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1950,int(minage)),attrs={'class': 'Date of birth','style':'width: 33%; height: 4%;'}))
    file = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control ProfilePic'}))
    hobbies = forms.MultipleChoiceField(choices=hobbyList,widget=forms.CheckboxSelectMultiple(attrs={'class': 'hobbies'}))

# A form for the editprofile.html page
class EditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        genders=Gender.objects.all()
        genderList = []
        for gen in genders:
            genderList.append((gen.pk,gen.name))

        hobb=Hobby.objects.all()
        hobbyList = []
        for hobs in hobb:
            hobbyList.append((hobs.pk,hobs.name))

        now = D.datetime.utcnow()
        minAge = D.timedelta(seconds=365 * 24 * 60 * 60 * 17)
        delta = now - minAge
        format = "%Y"
        minage = D.datetime.strftime(delta, format)
        user = kwargs.pop('data', None)

        # gets current user hobbies and displayed it as checked list
        userHobbies = []
        for hobs in user.hobbies.all():
            userHobbies.append(hobs.pk)

        super(EditForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.CharField(required=False,widget=forms.EmailInput(attrs={'value': user.email, 'class':'form-control'}))
        self.fields['gender'] = forms.ChoiceField(required=False,choices=genderList,initial=user.gender.pk ,widget=forms.Select(attrs={'autocomplete':'off','class':'form-control'}))
        self.fields['file'] = forms.ImageField(required=False,widget=forms.FileInput(attrs={'class': 'form-control ProfilePic'}))
        self.fields['hobbies'] = forms.MultipleChoiceField(required=False,initial=userHobbies,choices=hobbyList,widget=forms.CheckboxSelectMultiple(attrs={}))
