from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model() 

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=100, label='이름')
    email = forms.EmailField(label='이메일')
    region = forms.CharField(max_length=50, required=False, label='지역')
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        labels = {
            'username': '아이디',
            'password1': '비밀번호',
            'password2': '비밀번호 확인',
        }
        help_texts = {
            'username': '150자 이하 문자, 숫자, @/./+/-/_만 가능합니다.',
            'password1': '',
            'password2': '동일한 비밀번호를 다시 입력해주세요.',
        }
