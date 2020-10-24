from django import forms
from django.contrib.auth.hashers import check_password

from user.services.user_service import UserService


class RegisterUserForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', max_length=255)
    confirm_password = forms.CharField(
        label='Confirm Password', max_length=255)
    username = forms.CharField(label='Username', max_length=20)
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        'email_exist': ("User with this email is already registered."),
        'username_exist': ("User with this username already exists, try something else.")
    }
    
    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )

        return confirm_password
    
    def clean_email(self):
        email = self.cleaned_data.get("email")

        user_service = UserService()
        if user_service.does_user_exist(email=email):
            raise forms.ValidationError(
                self.error_messages['email_exist'],
                code='email_exist',
            )
        
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")

        user_service = UserService()
        if user_service.does_user_exist(username=username):
            raise forms.ValidationError(
                self.error_messages['username_exist'],
                code='username_exist',
            )
        
        return username


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', max_length=255)
    error_messages = {
        'email_unregistered': ("The email is not registered."),
        'incorrect_password': ("Password is incorrect.")
    }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        user_service = UserService()
        user = user_service.get_user(email=email)
        if user is None:
            self.add_error(
                'email',
                self.error_messages['email_unregistered']
            )

            return
        
        if not check_password(password, user.password):
            self.add_error(
                'password',
                self.error_messages['incorrect_password']
            )
            
            return

        return cleaned_data


class MagicLinkForm(forms.Form):
    email = forms.EmailField(label='Email')
    error_messages = {
        'email_unregistered': ("The email is not registered.")
    }

    def clean_email(self):
        email = self.cleaned_data.get("email")

        user_service = UserService()
        if not user_service.does_user_exist(email=email):
            raise forms.ValidationError(
                self.error_messages['email_unregistered'],
                code='email_unregistered',
            )
        
        return email
