from django import forms
from KuberaApp.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    # Override the username field
    username = forms.CharField(label="Mobile Number", max_length=15)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email','upi_id', 'google_pay_number','phonepe_number']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match.")
        return confirm_password

from .models import OrderCreation

class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = OrderCreation
        fields = ['board', 'numbers']


class DepositForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=300, decimal_places=2)
    transaction_id = forms.CharField(label='Transaction Reference ID', max_length=255)
    # upi_address = forms.CharField(label='UPI Address', max_length=255)

class BankInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['upi_id', 'paytm_number', 'phonepe_number', 'google_pay_number', 'bank_holder_name', 'bank_account_number', 'bank_ifsc_code']