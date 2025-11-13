from django import forms
from .models import FinancialTermCard, Meeting, MeetingInvitation

class FinancialTermCardForm(forms.ModelForm):
    class Meta:
        model = FinancialTermCard
        fields = ['term', 'description', 'example'] 


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'description', 'meeting_type', 'start_time', 'end_time', 'join_url', 'participants']


class MeetingInvitationForm(forms.ModelForm):
    class Meta:
        model = MeetingInvitation
        fields = ['email', 'invitee']