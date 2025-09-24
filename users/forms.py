from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        # Убрали role из полей регистрации


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Пароль"
    )