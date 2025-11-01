from django import forms
from .models import Voter, Candidate, AdminUser

class VoterRegistrationForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})  # ✅ this adds calendar input
    )
    class Meta:
        model = Voter
        fields = ['name', 'father_name', 'birth_date', 'voter_card_id', 'password', 'constituency']
        widgets = {
            'password': forms.PasswordInput()
        }

class CandidateRegistrationForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'party_name', 'constituency', 'age', 'qualifications', 'promises', 'election_symbol', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

class AdminLoginForm(forms.Form):
    gov_id = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())

class VoterLoginForm(forms.Form):
    voter_card_id = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())
