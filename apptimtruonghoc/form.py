from django import forms
from allauth.account.forms import SignupForm
from .models import User # Import User model của bạn




class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'date_of_birth', 'living_place', 'user_level', 'user_photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
