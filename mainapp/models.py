from django.contrib.auth.models import User
from django.db import models

class Gender(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
# Profiles will have an image and date of birth
# that a Member might or might not have, hence the
# OneToOne relationship in Member with null=True
class Profile(models.Model):
    image = models.ImageField(upload_to="profile_images")
    dob = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return str(self.dob)

# Django's User model already has username, password, email
# both of which are required fields, so Member inherits
# these fields
class Member(User):
    profile = models.OneToOneField(
        to=Profile,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    hobbies = models.ManyToManyField(
        to='Hobby',
        blank=True,
        symmetrical=False,
        related_name='related_to'
    )
    likes = models.ManyToManyField(
        to='self',
        blank=True,
        symmetrical=True
    )
    gender = models.ForeignKey('Gender', on_delete=models.CASCADE)

    def __str__(self):
        return self.username

class Hobby(models.Model):
    name = models.CharField(max_length=254)
    desc = models.CharField(max_length=254)


    def __str__(self):
        return self.name
