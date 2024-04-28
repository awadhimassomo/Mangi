from django import forms


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    PhoneNumber = forms.EmailField(max_length=50, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Phone-Number'}))
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))