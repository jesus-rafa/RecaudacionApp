from applications.users.models import User
from django import forms
from django.contrib.auth import authenticate


class UserForm(forms.ModelForm):
    username = forms.CharField(
        label='Usuario',
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Usuario',
                'class': 'web form-control',
                'style': 'display: none'

            }
        )
    )

    email = forms.CharField(
        label='Email',
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Usuario',
                'class': 'web form-control',
                'style': 'display: none'

            }
        )
    )

    nombres = forms.CharField(
        label='Nombres',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'style': 'display: none'

            }
        )
    )

    apellidos = forms.CharField(
        label='Apellidos',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'style': 'display: none'

            }
        )
    )

    telefono = forms.CharField(
        label='Telefono:',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder': ' '
            }
        )
    )

    ext = forms.CharField(
        label='Ext:',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder': ' '
            }
        )
    )

    avatar = forms.FileField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = User
        fields = ["username", "email", "nombres",
                  "apellidos", "telefono", "ext", "avatar"]


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Correo:',
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Correo',
                'class': 'form-control input-rec float-label',
            }
        )
    )

    password = forms.CharField(
        label='Contraseña:',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Contraseña',
                'class': 'Password form-control input-rec float-label',
            }
        )
    )

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        if not authenticate(email=username, password=password):
            raise forms.ValidationError(
                'Los datos del usuario no son correctos')

        return self.cleaned_data


class BatchForm(forms.Form):
    archivo = forms.FileField(required=True)
