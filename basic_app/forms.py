from django import forms
from django.contrib.auth.models import User
from basic_app.models import UserProfileInfo

class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput())

    class Meta():
        model = User
        fields = ['username', 'email', 'password']
        help_texts = {
            'username':"Must be your 7 digit student number",
        }

class UserProfileInfoForm(forms.ModelForm):
    class Meta():
        model = UserProfileInfo
        fields = ['date_of_birth']
        help_texts = {
            'date_of_birth':'optional'
        }
